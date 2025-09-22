import asyncio
import math

from adrf.decorators import api_view
from bento_lib.discovery import SearchSection, DiscoveryEntity
from collections import defaultdict
from django.core.exceptions import FieldError, ValidationError
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema, inline_serializer
from functools import partial
from operator import is_not
from rest_framework import serializers, status
from rest_framework.decorators import permission_classes
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response
from structlog.stdlib import BoundLogger

from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.authz.permissions import BentoAllowAny, BentoDeferToHandler
from chord_metadata_service.authz.types import DataPermissions, DataTypeDiscoveryPermissions
from chord_metadata_service.chord import data_types as dts
from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope
from chord_metadata_service.logger import logger
from chord_metadata_service.restapi.pagination import DEFAULT_PAGE_SIZE, DEFAULT_MAX_PAGE_SIZE
from chord_metadata_service.restapi.responses import bad_request, not_found
from chord_metadata_service.utils import build_id_set

from . import responses as dres
from .censorship import get_rules, get_threshold, thresholded_count
from .constants import DISCOVERY_ENTITIES
from .exceptions import DiscoveryEmptyException, DiscoveryScopeException
from .fields import get_field_options, get_range_stats, get_categorical_stats, get_date_stats
from .fields_utils import normalize_field_path_true_model
from .filtering import discovery_filter_queryset
from .full_text_search import full_text_search_vector
from .matches import DISCOVERY_ENTITY_TO_MATCH_FN
from .model_lookups import DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE
from .pydantic_models import (
    DiscoveryFieldResponse,
    DiscoveryFieldResponses,
    DiscoveryResponse,
    BinList,
    DiscoveryFieldAndOptions,
    DiscoverySearchSectionWithOptions,
    DiscoverySearchFieldsResponse,
    DiscoveryPagination,
    DiscoveryQuery,
    DiscoveryMatches,
    DiscoveryMatchesPaginatedResponse,
)
from .responses import INSUFFICIENT_DATA_AVAILABLE_MSG
from .schemas import DISCOVERY_SCHEMA
from .scope import get_request_discovery_scope
from .utils import (
    get_discovery_data_type_permissions,
    get_discovery_field_set_permissions,
    empty_discovery,
    get_discovery_entity_model_scoped_queryset,
)

is_not_none = partial(is_not, None)


QueryExecutionResult = tuple[QuerySet, frozenset[DiscoveryEntity]]


class QueryQuerysetsCache:
    """
    Cache definition for a specific query, in the context of a specific request (--> scope, permissions).
    It takes a bit of effort to build the Django queryset from field definitions/a query object, and there are specific
    cases were we may be doing this many times, so we might as well re-use the work done.
    """

    def __init__(
        self,
        query: DiscoveryQuery,
        scope: ValidatedDiscoveryScope,
        dt_permissions: DataTypeDiscoveryPermissions,
        lg: BoundLogger,
    ):
        self._query: DiscoveryQuery = query
        self._scope: ValidatedDiscoveryScope = scope
        self._dt_permissions: DataTypeDiscoveryPermissions = dt_permissions
        self._queryset_cache: dict[DiscoveryEntity, QueryExecutionResult] = {}
        self._queryset_locks = defaultdict(asyncio.Lock)

        self._logger: BoundLogger = lg

    async def _execute_discovery_query(
        self, queryset_entity: DiscoveryEntity, lg: BoundLogger | None, validate_field: bool
    ) -> QueryExecutionResult:
        queryset = get_discovery_entity_model_scoped_queryset(queryset_entity, self._scope)

        if fts := self._query.fts:
            ids_set = await build_id_set(
                queryset.annotate(search=full_text_search_vector(queryset_entity)).filter(search=fts),
                field="id",
            )
            # When this is done as a subquery, it destroys performance (perhaps fixable with a PG version > 13?)
            #  - but ONLY when we have specified a scope (project/dataset), I guess due to some kind of prefetching or
            #    join? it's unclear, but for now we just do this ugly thing instead.
            queryset = queryset.filter(id__in=ids_set)

        # May raise:
        #  - DiscoveryEmptyException
        #  - ValidationError
        filtered_queryset, queried_entities = await discovery_filter_queryset(
            self._scope,
            self._query,
            queryset_entity,
            queryset,
            self._dt_permissions,
            lg or self._logger,
            validate_field=validate_field,
        )

        return filtered_queryset, queried_entities

    async def get_query_queryset_and_queried_entities(
        self,
        entity: DiscoveryEntity,
        lg: BoundLogger | None = None,
        validate_field: bool = True,
    ) -> tuple[QuerySet, frozenset[DiscoveryEntity]]:
        # We use an async lock here to prevent executing the same entity query multiple times if we have parallel async
        # requests happening (liable to happen with field-level data collection in discovery_field_response, where we do
        # an asyncio.gather across all the fields).
        # Combining the lock with the caching mechanism means this is roughly equivalent to re-using the same
        # "promise"/awaitable if one already exists.
        async with self._queryset_locks[entity]:
            if entity not in self._queryset_cache:
                await (lg or self._logger).adebug(
                    "QueryQuerysetsCache executing query", entity=entity, cache_keys=tuple(self._queryset_cache.keys())
                )
                res = await self._execute_discovery_query(entity, lg, validate_field=validate_field)
                self._queryset_cache[entity] = res
                return res

            return self._queryset_cache[entity]


@extend_schema(
    description="Discovery search fields with their configuration",
    responses={
        status.HTTP_200_OK: inline_serializer(
            name='discovery_search_fields_response',
            fields={'sections': serializers.JSONField()}
        ),
        status.HTTP_404_NOT_FOUND: inline_serializer(
            name='discovery_search_fields_not_configured',
            fields={'message': serializers.CharField()},
        ),
    }
)
@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def discovery_search_fields(request: DrfRequest):
    """
    get:
    Return discovery search fields with their configuration
    """

    try:
        scope: ValidatedDiscoveryScope = await get_request_discovery_scope(request)
    except DiscoveryScopeException as e:
        return not_found(request, e.message)

    if empty_discovery(scope):
        return Response(dres.NO_PUBLIC_FIELDS_CONFIGURED, status=status.HTTP_404_NOT_FOUND)

    dt_permissions = await get_discovery_data_type_permissions(request, scope)

    discovery = scope.discovery
    _, field_permissions = get_discovery_field_set_permissions(discovery, None, dt_permissions)

    # ------------------------------------------------------------------------------------------------------------------

    queryset_entity: DiscoveryEntity = "phenopacket"
    queryset = get_discovery_entity_model_scoped_queryset(queryset_entity, scope)

    # ------------------------------------------------------------------------------------------------------------------

    # Note: the array is wrapped in a dictionary structure to help with JSON
    # processing by some services.

    async def _get_field_response(field: str) -> DiscoveryFieldAndOptions | None:
        field_props = discovery.fields.get(field, {})
        field_perms = field_permissions[field]

        if not field_perms.counts:  # Cannot even see counts, skip this field  TODO: incorporate booleans
            return None

        return DiscoveryFieldAndOptions(
            id=field,
            definition=field_props,
            options=await get_field_options(queryset_entity, queryset, field, scope, field_permissions[field]),
        )

    async def _get_section_response(section: SearchSection) -> DiscoverySearchSectionWithOptions | None:
        section_fields = list(filter(is_not_none, await asyncio.gather(*map(_get_field_response, section.fields))))

        if not section_fields:
            # No access to any field in the section (they were all None -> they all got filtered out), so we want to
            # filter the section itself out - return a None which will get filtered out below.
            return None

        return DiscoverySearchSectionWithOptions(section_title=section.section_title, fields=section_fields)

    return Response(DiscoverySearchFieldsResponse(
        sections=list(filter(is_not_none, await asyncio.gather(*map(_get_section_response, discovery.search))))
    ))


async def discovery_field_response(
    qqs: QueryQuerysetsCache,
    scope: ValidatedDiscoveryScope,
    field: str,
    dt_permissions: DataTypeDiscoveryPermissions,
    lg: BoundLogger,
) -> DiscoveryFieldResponse | None:
    lg = lg.bind(field=field)

    field_props = scope.discovery.fields[field]
    field_entity, field_entity_path = normalize_field_path_true_model(*field_props.get_entity_and_field_path())
    field_perms: DataPermissions = dt_permissions[DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE[field_entity]]

    if not field_perms.counts:
        # We cannot compute stats right now for boolean-level responses. Thus, if we do not have at least counts
        # permissions, we return None and this presumably gets filtered out, resulting in this field response not
        # being present in the discovery response. Then, it's up to the API consumer (e.g., the front end) to handle
        # this with relative grace (not show a chart/search field, ...).
        return None

    # We cannot re-validate the field against its options here, as it can trip up "invalid options" due to small cell
    # counts if we're in a nested entity.
    #  => For example, if we have 10 individuals with 2 biosamples after querying, and our field entity is a
    #     biosample but our query is on an individual, we may get a small cell count issue through biosample but not if
    #     we're going through individual (we may have five FEMALE individuals, but only one with a biosample).
    queryset, _ = await qqs.get_query_queryset_and_queried_entities(field_entity, lg, validate_field=False)

    stats: BinList

    try:
        if field_props.datatype == "string":
            stats = await get_categorical_stats(scope, field_entity, queryset, field_props.root, field_perms)
        elif field_props.datatype == "number":
            stats = await get_range_stats(scope, field_entity, queryset, field_props.root, field_perms)
        elif field_props.datatype == "date":
            stats = await get_date_stats(scope, field_entity, queryset, field_props.root, field_perms)
        else:  # pragma: no cover
            # Can't actually occur with Pydantic implementation of the discovery configuration model, which will
            # validate the data_type value.
            raise NotImplementedError()
    except FieldError as e:
        await lg.aexception("discovery_field_response field error", exc_info=e)
        # We return None and this field presumably gets filtered out, with logs on the backend
        # TODO: some type of field response error we can return to the front-end - a DiscoveryFieldResponse error prop?
        return None

    return DiscoveryFieldResponse(id=field, definition=field_props, data=stats)


async def discovery_queryset_entity_counts(qqs: QueryQuerysetsCache) -> dict[DiscoveryEntity, int]:
    """
    Returns a dictionary of discovery entity counts for a given scope/query context (i.e., a given QueryQuerysetsCache
    instance). In other words, for each discovery entity, we'll get a queryset of the query executed on the entity and
    count the number of matching entities.
    """

    async def _get_entity_count(ee: DiscoveryEntity) -> int:
        # We cannot re-validate the field against its options here, as it can trip up "invalid options" due to small
        # cell counts if we're in a nested entity.
        #  => For example, if we have 10 individuals with 2 biosamples after querying, and our field entity is a
        #     biosample but our query is on an individual, we may get a small cell count issue through biosample but not
        #     if we're going through individual (we may have five FEMALE individuals, but only one with a biosample).
        #
        # We access [0] of the result of get_query_queryset_and_queried_entities because it returns a tuple of
        # (queryset, frozenset of queried entities), but we only need the former (to get the count).
        return await (await qqs.get_query_queryset_and_queried_entities(ee, validate_field=False))[0].acount()

    return {
        e: ec
        for e, ec in zip(
            DISCOVERY_ENTITIES,
            await asyncio.gather(*(_get_entity_count(e) for e in DISCOVERY_ENTITIES)),
        )
    }


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def discovery_endpoint(request: DrfRequest):
    """
    get:
    Overview, optionally filtered by fields, of phenopackets+experiments data.
    """

    # Get the request discovery scope, which we'll use to narrow down the project/dataset for discovery
    # charts/filtering.
    try:
        scope = await get_request_discovery_scope(request)
    except DiscoveryScopeException as e:
        return not_found(request, e.message)

    lg = logger.bind(scope_repr=repr(scope))

    # If the discovery object is "empty", i.e., no fields/charts/filters specified, this endpoint becomes a 404, here
    # meaning no data could be found for discovery purposes.
    if empty_discovery(scope):
        return dres.no_public_data(request)

    dt_permissions = await get_discovery_data_type_permissions(request, scope)
    if not any(d.bool_ for d in dt_permissions.values()):
        # At minimum, we need some bool permissions for data types in order to view True/False for having a specific
        # entity above the count threshold.
        return dres.insufficient_privileges(request)

    # -- Query execution -----------------------------------------------------------------------------------------------

    # Above, we checked for at minimum one boolean permission for data, since we can skip returning any counts data for
    # fields where we do not have permissions, relying on the front end/API consumer to handle this case.
    # HOWEVER, if we're doing any querying, we will end up needing at least boolean permissions for ALL FIELDS (i.e.,
    # their respective DATA TYPES) queried. Thus, if we're querying, the above check IS NOT SUFFICIENT!
    #  --> this actual second permissions check happens inside the following function stack right now, and raises a
    #      ValidationError:
    #        QueryQuerysetsCache
    #         --> _execute_discovery_query
    #         --> discovery_filter_queryset
    #         --> the overall_permissions.bool_ check

    queryset_entity: DiscoveryEntity = "phenopacket"

    try:
        query = DiscoveryQuery.from_drf_request(request)
        lg = lg.bind(queried_entity=queryset_entity, query=query.model_dump(mode="json"))
        qqs = QueryQuerysetsCache(query, scope, dt_permissions, lg)
        queryset, queried_entities = await qqs.get_query_queryset_and_queried_entities(queryset_entity)
    except DiscoveryEmptyException:
        return dres.no_public_data(request)
    except ValidationError as e:
        return await dres.django_validation_error(request, e, lg, "discovery endpoint encountered validation error")

    # -- Field responses -----------------------------------------------------------------------------------------------

    discovery = scope.discovery
    fields: tuple[str, ...] = discovery.get_chart_field_ids()

    field_responses: DiscoveryFieldResponses = DiscoveryFieldResponses.model_validate({
        field: field_res
        for field, field_res in zip(
            fields,
            await asyncio.gather(
                *(
                    discovery_field_response(qqs, scope, field, dt_permissions, lg)
                    for field in fields
                )
            )
        )
        if field_res is not None
        # Parallel async collection of field responses for public overview
    })

    # -- Counts processing ---------------------------------------------------------------------------------------------

    message: str = ""
    counts: dict[DiscoveryEntity, int] = await discovery_queryset_entity_counts(qqs)

    # for each 'discovery entity', we generate either:
    #  - a count (0/count-if-above-threshold), or
    #  - a boolean (count > threshold)
    count_or_bools_res: dict[DiscoveryEntity, int | bool] = {}

    # TODO: permissions non-hard-coded
    for e in counts:
        dt = DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE[e]
        entity_permissions = dt_permissions[dt]
        count_threshold = get_threshold(discovery, entity_permissions)

        entity_count = counts[e]

        # Extra check for threshold being above 0 to not log warnings for true-0 counts with query:data
        if 0 < counts[e] <= count_threshold and count_threshold > 0:
            await lg.ainfo("discovery: entity count is below threshold", entity=e, threshold=count_threshold)
            entity_count = 0  # censor sub-threshold counts to 0

        if entity_permissions.any_permissions():  # if we have any permissions, then add a response for the overview
            # if we only have boolean permissions, store a Boolean "count" (yes or no to above-threshold count) if we
            # didn't get censored down to 0 above.
            # This key used to be a plural version of the public model name, but is now singular so we have a consistent
            # key to use across all discovery endpoints:
            count_or_bools_res[e] = entity_count if entity_permissions.counts else (entity_count > 0)

    if (
        not count_or_bools_res[queryset_entity]
        and not dt_permissions[DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE[queryset_entity]].data
    ):
        message = INSUFFICIENT_DATA_AVAILABLE_MSG

    # If phenopacket is 0, don't reveal nested entities exist, otherwise we could get responses like (in the case of
    # one phenopacket with five biosamples): { phenopacket: 0, biosample: 5, ... }
    # TODO: !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # -- Discovery structured event logging ----------------------------------------------------------------------------

    await lg.ainfo("discovery executed", counts=counts)

    # -- Build and return discovery response ---------------------------------------------------------------------------

    return Response(
        DiscoveryResponse(
            layout=discovery.overview,
            fields=field_responses,
            root_entity=queryset_entity,
            queried_entities=queried_entities,
            message=message,
            # permissions-dependent: dictionary of {entity: counts or True if above threshold, 0/False otherwise}:
            counts=count_or_bools_res,
        )
    )


@api_view(["GET"])
@permission_classes([BentoDeferToHandler])
async def discovery_matches(request: DrfRequest):
    """
    Returns a paginated result-set of entity matches for a discovery query. For a given query, this endpoint can return
    different entities at the top-level using the _entity parameter.

    Query parameters:
      /^[^_].*$/: Discovery field filters, like discovery_endpoint above
      _entity:    Entity to return in result-set. phenopacket|individual|biosample|experiment|experiment_result
      _page:      Page number, 0-indexed integer; defaults to 0
      _page_size: Page size; defaults to 25
      project:    Discovery scope - project ID (if not set, the global scope is used)
      dataset:    Discovery scope - dataset ID (if not set, the project or global scope is used)

    Note on query parameter names:
      - QueryQuerysetsCache._execute_discovery_query calls build_discovery_query_from_request, which grabs every query
        parameter except "project", "dataset", and those starting with "_" and tries to find fields to query.
        By separating the namespace for discovery filter query parameters from "other" query parameters by prefixing
        other query parameters with _, we eliminate possible ambiguities between discovery fields.
    """

    # TODO: DEDUPLICATE

    # Get the request discovery scope, which we'll use to narrow down the project/dataset for discovery
    # charts/filtering.
    try:
        scope = await get_request_discovery_scope(request)
    except DiscoveryScopeException as e:
        return not_found(e.message)

    lg = logger.bind(scope_repr=repr(scope))

    # If the discovery object is "empty", i.e., no fields/charts/filters specified, this endpoint becomes a 404, here
    # meaning no data could be found for discovery purposes.
    if empty_discovery(scope):
        return dres.no_public_data(request)

    dt_permissions = await get_discovery_data_type_permissions(request, scope)
    if not dt_permissions[dts.DATA_TYPE_PHENOPACKET].data:
        # "Extra" permissions check vs. regular discovery endpoint: we need full data permissions
        return dres.insufficient_privileges(request)
    authz_middleware.mark_authz_done(request)

    # -- Query execution -----------------------------------------------------------------------------------------------

    queried_entity: DiscoveryEntity = request.query_params.get("_entity", "phenopacket")
    if queried_entity not in DISCOVERY_ENTITIES:
        return bad_request(request, "invalid entity")

    lg = lg.bind(queried_entity=queried_entity)

    try:
        query = DiscoveryQuery.from_drf_request(request)
        qqs = QueryQuerysetsCache(query, scope, dt_permissions, lg)
        queryset, _ = await qqs.get_query_queryset_and_queried_entities(queried_entity)
    except DiscoveryEmptyException:
        return dres.no_public_data(request)
    except ValidationError as e:
        return await dres.django_validation_error(
            request, e, lg, "discovery matches endpoint encountered validation error"
        )

    lg = lg.bind(query=query.model_dump(mode="json"))

    # -- Pagination ----------------------------------------------------------------------------------------------------

    page: int = 0
    page_size: int = DEFAULT_PAGE_SIZE

    try:
        page: int = int(request.query_params.get("_page", str(page)))
    except ValueError:
        return bad_request(request, "bad page")

    try:
        # if page_size is set to 0, all records will be returned.
        # if page_size is less than 0, it will be set to 0; if it is greater than DEFAULT_MAX_PAGE_SIZE, it'll be set
        #  to that value.
        page_size = min(max(int(request.query_params.get("_page_size", str(page_size))), 0), DEFAULT_MAX_PAGE_SIZE)
    except ValueError:
        return bad_request(request, "bad page size")

    total_count = await queryset.acount()

    if page < 0 or (page_size and total_count and page >= math.ceil(total_count / page_size)):
        return bad_request(request, "bad page")

    pagination = DiscoveryPagination(page=page, page_size=page_size, total=total_count)
    lg = lg.bind(pagination=pagination.model_dump(mode="json"))

    if page_size > 0:
        matches_page = queryset[page * page_size:(page + 1) * page_size] if page_size > 0 else queryset[:]
    else:
        matches_page = queryset[:]

    # -- Log discovery match page fetch event --------------------------------------------------------------------------

    # structured event logging for discovery: embed search details
    await lg.ainfo("discovery matches requested")

    # -- Build and return response -------------------------------------------------------------------------------------

    return Response(
        DiscoveryMatchesPaginatedResponse(
            results_entity=queried_entity,
            results=DiscoveryMatches(
                root=await DISCOVERY_ENTITY_TO_MATCH_FN[queried_entity](matches_page, scope, dt_permissions, True, {})
            ),
            pagination=pagination,
        ).model_dump(mode="json", exclude_unset=True)
    )


# TODO: extend this implementation for Bento v20+
@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def discovery_ui_hints(request: DrfRequest):
    """
    Endpoint for returning miscellaneous UI hints for any front-end which consumes the various discovery endpoints.
    For example:
     - indications of which elements should be hidden in the front end, to avoid a bunch of ugly disabled elements for
       projects/datasets which don't have any intention of ingesting, e.g., experiment data or geographical data.
     - indications of the presence of certain types of data, e.g1., geographical data, to encourage API consumers to
       render a certain element (e.g., a map).
    """

    try:
        scope = await get_request_discovery_scope(request)
    except DiscoveryScopeException as e:
        return not_found(request, e.message)

    lg = logger.bind(scope_repr=repr(scope))

    dt_permissions = await get_discovery_data_type_permissions(request, scope)

    # TODO: support querying?
    qqs = QueryQuerysetsCache(DiscoveryQuery(fts=None, filters={}), scope, dt_permissions, lg)
    counts = await discovery_queryset_entity_counts(qqs)

    return {
        # This helps the UI determine which entities are available in a particular scope, so we can hide entities with
        # no data ingested (e.g., not showing experiments for an instance with only phenopackets). Because of this
        # purpose, we don't filter it beforehand - we still want to see 0 counts if they're the result of a specific
        # search, but we don't want them
        "entities_with_data": [
            e for e, v in counts.items()
            if thresholded_count(v, scope, dt_permissions[DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE[e]])
        ],
        # TODO: implement something like this for hinting towards maps
        # TODO: instead of this, maybe we also collect experiment results and check for geojson, and indicate if we
        #  should present a consolidated map view?
        # "biosample_location_present": False,  # TODO: non-Null location_collected above threshold
    }


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def discovery_schema(_request: DrfRequest):
    """
    Endpoint for the discovery configuration schema, derived from the DiscoveryConfig Pydantic model with an ID injected
    into it (see schemas.py).
    """
    return Response(DISCOVERY_SCHEMA)


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def discovery_rules(request: DrfRequest):
    """
    Endpoint for censorship / display rules (count threshold, maximum query parameters).
    Returns a serialization of the DiscoveryConfigRules object from bento_lib.discovery.models.config
    """

    try:
        discovery_scope = await get_request_discovery_scope(request)
    except DiscoveryScopeException as e:
        return not_found(request, e.message)

    dt_permissions = await get_discovery_data_type_permissions(request, discovery_scope)

    # TODO: allow filtering by fields accessed?
    fs_permissions, _ = get_discovery_field_set_permissions(discovery_scope, None, dt_permissions)

    return Response(get_rules(discovery_scope, data_permissions=fs_permissions), status=status.HTTP_200_OK)
