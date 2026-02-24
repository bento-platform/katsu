import asyncio
import math

from adrf.decorators import api_view
from asgiref.sync import sync_to_async
from bento_lib.discovery import SearchSection, DiscoveryEntity
from bento_lib.responses import errors
from collections import defaultdict
from django.core.exceptions import FieldError, ValidationError
from django.db.models import QuerySet, Q, Case, When, Subquery, OuterRef
from django.db.models.functions import Greatest
from drf_spectacular.utils import extend_schema, inline_serializer
from functools import partial, wraps
from operator import is_not
from rest_framework import serializers, status
from rest_framework.decorators import permission_classes, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response
from structlog.stdlib import BoundLogger
from typing import Any, Awaitable, Callable, Literal, overload

from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.authz.permissions import BentoAllowAny, BentoDeferToHandler
from chord_metadata_service.authz.types import DataPermissions, DataTypeDiscoveryPermissions
from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope
from chord_metadata_service.logger import logger
from chord_metadata_service.restapi.api_renderers import PassThruCSVRenderer
from chord_metadata_service.restapi.pagination import DEFAULT_PAGE_SIZE, DEFAULT_MAX_PAGE_SIZE
from chord_metadata_service.utils import build_id_set

from . import responses as dres
from .censorship import get_rules, censor_entity_counts
from .constants import DISCOVERY_ENTITIES
from .exceptions import DiscoveryScopeException
from .field_paths.resolve import resolve_filter_mapping_to_queryset_model
from .fields import get_field_options, get_range_stats, get_categorical_stats, get_date_stats
from .field_paths.normalize import normalize_field_path_true_model
from .filtering import discovery_filter_queryset
from .full_text_search import trigram_similarity_search, normal_full_text_search, build_rank_dict, \
    normal_full_text_search_annotations, trigram_similarity_search_annotations, TRIGRAM_MINIMUM_SIMILARITY
from .matches import DISCOVERY_ENTITY_TO_MATCH_FN, DISCOVERY_ENTITY_TO_CSV_RENDERER
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
    DiscoveryUIHintsResponse,
)
from .schemas import DISCOVERY_SCHEMA
from .scope import get_request_discovery_scope
from .types import (
    EntityCountOrBoolResponse, EntityCounts, DiscoveryResponseFormat, AcceptedDiscoveryResponseFormats, FTSType
)
from .utils import (
    get_discovery_data_type_permissions,
    get_discovery_field_set_permissions,
    empty_discovery,
    get_discovery_entity_model_scoped_queryset,
)

is_not_none = partial(is_not, None)


QueryExecutionResult = tuple[QuerySet, frozenset[DiscoveryEntity]]

EMPTY_DISCOVERY_QUERY = DiscoveryQuery()


class QueryHelper:
    """
    Helper class and caching object for a specific query, in the context of a specific request (--> scope, permissions).

    Justifications:
     - encapsulate data/methods that operate on (query, scope, dt_permissions).
     - cache constructed querysets for a particular instance of the above combination:
         It takes a bit of effort to build the Django queryset from field definitions/a query object, and there are
         specific cases were we may be doing this many times, so we might as well re-use the work done.
     - cache intermediate data used during full-text searching
    """

    def __init__(
        self,
        query: DiscoveryQuery | None,
        scope: ValidatedDiscoveryScope,
        dt_permissions: DataTypeDiscoveryPermissions,
        lg: BoundLogger,
    ):
        self._query: DiscoveryQuery = query or EMPTY_DISCOVERY_QUERY
        self._scope: ValidatedDiscoveryScope = scope
        self._dt_permissions: DataTypeDiscoveryPermissions = dt_permissions

        # Cache dictionary for constructed querysets for executed queries
        # + corresponding locks for accessing/cache manipulation:
        self._queryset_cache: dict[DiscoveryEntity, QueryExecutionResult] = {}
        self._queryset_locks = defaultdict(asyncio.Lock)

        # Cache dictionary for full-text searches (and corresponding locks for accessing/cache manipulation) with:
        #  - keys being (discovery entity, search query, FTS search type)
        #  - values being sets of IDs of objects of the same type as the discovery entity in the key.
        self._fts_cache: dict[tuple[DiscoveryEntity, str, FTSType], dict] = {}
        self._fts_cache_locks = defaultdict(asyncio.Lock)

        # Cache: entity counts for the scope+permissions+query combination; populated by a call to _get_entity_counts
        self._entity_counts: EntityCounts | None = None

        # Cache: entities with data for the scope (not applying the query);
        # populated by a call to get_scope_entities_with_data()
        self._scope_entities_with_data: frozenset[DiscoveryEntity] | None = None

        self._logger: BoundLogger = lg

    @property
    def scope(self) -> ValidatedDiscoveryScope:
        return self._scope

    @property
    def dt_permissions(self) -> DataTypeDiscoveryPermissions:
        return self._dt_permissions

    @staticmethod
    def _qs_fts(fts_entity: DiscoveryEntity, qs: QuerySet, query: str, fts_type: FTSType) -> QuerySet:
        return (
            trigram_similarity_search(fts_entity, qs, query)
            if fts_type == "trigram"
            else normal_full_text_search(fts_entity, qs, query, fts_type)
        )

    async def _get_fts_ids_and_rank(
        self, root_entity: DiscoveryEntity, fts_entity: DiscoveryEntity, query: str, fts_type: FTSType
    ) -> dict:
        """
        Given a discovery entity to execute a full-text search on, a full-text query search string, and a full-text
        search query type, this function executes the search and caches matching IDs in the _fts_cache private property
        of the object for use in executing a discovery query.
        """
        k = (fts_entity, query, fts_type)
        qs = get_discovery_entity_model_scoped_queryset(fts_entity, self._scope)
        async with self._fts_cache_locks[k]:
            if k not in self._fts_cache:
                self._fts_cache[k] = await build_rank_dict(
                    self._qs_fts(fts_entity, qs, query, fts_type),
                    resolve_filter_mapping_to_queryset_model(fts_entity, root_entity, ("pk",)),
                    (fts_entity, root_entity),
                )
            return self._fts_cache[k]

    async def _execute_discovery_query(
        self, queryset_entity: DiscoveryEntity, lg: BoundLogger | None, validate_field: bool
    ) -> QueryExecutionResult:
        queryset = get_discovery_entity_model_scoped_queryset(queryset_entity, self._scope)

        fts_queried_entities = frozenset()
        fts_ids_rank_dict = {}  # if FTS is executed, this contains {pk: rank [higher --> sorted earlier]}

        if fts := self._query.fts:  # Execute FTS if self._query.fts is not ""
            # Each entity has a corresponding FTS vector we'll use, but querying using this doesn't query across
            # discovery entity boundaries. In order to get result sets for, e.g., phenopackets (with biosamples being
            # the entity with actual FTS matches), we need to build a query for the queryset checking nested biosamples
            # overlap with the ID set.

            fts_type = self._query.fts_type

            filters = Q()

            if fts_type == "trigram":
                filters = Q(max_rank__gte=TRIGRAM_MINIMUM_SIMILARITY)
            else:
                # TODO
                pass

            queryset = queryset.annotate(
                max_rank=Subquery(
                    queryset.filter(pk=OuterRef("pk")).annotate(
                        **(
                            trigram_similarity_search_annotations(queryset_entity, fts)
                            if fts_type == "trigram"
                            else normal_full_text_search_annotations(queryset_entity, fts, fts_type)
                        ),
                        **{
                            f"{fts_entity}__fts_rank": Subquery(
                                self._qs_fts(
                                    fts_entity,
                                    get_discovery_entity_model_scoped_queryset(fts_entity, self._scope),
                                    fts,
                                    fts_type,
                                ).filter(
                                    **{
                                        resolve_filter_mapping_to_queryset_model(fts_entity, queryset_entity,
                                                                                 ("pk",)): OuterRef("pk")
                                    }
                                ).values("rank")
                            )
                            for fts_entity in DISCOVERY_ENTITIES - {queryset_entity}
                        }
                    ).annotate(
                        max_rank=Greatest(
                            "rank", *(f"{e}__fts_rank" for e in DISCOVERY_ENTITIES - {queryset_entity})
                        )
                    ).values("max_rank")
                )
            ).filter(filters).order_by("-max_rank")

            # async for res in queryset:
            #     print(res.__dict__)

            # fts_ids_rank_dict = await self._get_fts_ids_and_rank(
            #     queryset_entity, queryset_entity, fts, self._query.fts_type
            # )
            # fts_filters = Q(pk__in=set(fts_ids_rank_dict.keys()))
            # for entity in DISCOVERY_ENTITIES - {queryset_entity}:
            #     e_ids_rank_dict = await self._get_fts_ids_and_rank(queryset_entity, entity, fts, self._query.fts_type)
            #
            #     # TODO; explain
            #     for e_pk, (qs_pks, rnk) in e_ids_rank_dict.items():
            #         print(e_pk, qs_pks, rnk)
            #         if qs_pks:
            #             for qs_pk in qs_pks:
            #                 if qs_pk in fts_ids_rank_dict:
            #                     fts_ids_rank_dict[qs_pk] = (
            #                         fts_ids_rank_dict[qs_pk][0],
            #                         max(fts_ids_rank_dict[qs_pk][1], rnk),
            #                     )
            #                 else:
            #                     fts_ids_rank_dict[qs_pk] = (qs_pks, rnk)
            #
            #     epk = resolve_filter_mapping_to_queryset_model(queryset_entity, entity, ("pk",))
            #     fts_filters |= Q(**{f"{epk}__in": set(e_ids_rank_dict.keys())})
            #
            # print(f"UPDATED for {queryset_entity}", fts_ids_rank_dict)
            #
            # # TODO: use the ID counts distribution here to return some hints for the UI as to where matches were found
            # #  or something. Although we currently have the same issue with filters, so we'll need to do some grand
            # #  unified thing for this.
            #
            # # When this is done as a subquery, it destroys performance (perhaps fixable with a PG version > 13?)
            # #  - but ONLY when we have specified a scope (project/dataset), I guess due to some kind of prefetching or
            # #    join? it's unclear, but for now we just do this ugly thing instead.
            # queryset = queryset.filter(fts_filters)
            # fts_queried_entities = await self.get_scope_entities_with_data()

        # May raise:
        #  - DiscoveryEmptyException
        #     although in all cases in these API calls this should be mitigated by an initial empty_discovery(...) check
        #  - ValidationError
        filtered_queryset, filter_queried_entities = await discovery_filter_queryset(
            self._scope,
            self._query,
            queryset_entity,
            queryset,
            self._dt_permissions,
            lg or self._logger,
            validate_field=validate_field,
        )

        # if fts_ids_rank_dict:
        #     filtered_queryset = filtered_queryset.annotate(
        #         final_rank=Case(
        #             *(When(pk=r_id, then=r_val) for r_id, (_, r_val) in fts_ids_rank_dict.items()),
        #             default=0.0,
        #         )
        #     ).order_by("-final_rank", "pk")
        # else:
        #     filtered_queryset = filtered_queryset.order_by("pk")

        return filtered_queryset, fts_queried_entities | filter_queried_entities

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
                    "QueryHelper executing query",
                    entity=entity,
                    query=self._query,
                    cache_keys=tuple(self._queryset_cache.keys()),
                )
                self._queryset_cache[entity] = await self._execute_discovery_query(
                    entity, lg, validate_field=validate_field
                )

            return self._queryset_cache[entity]

    async def _get_entity_counts(self) -> EntityCounts:
        """
        Returns a dictionary of discovery entity counts for a given scope/query context (i.e., a given QueryHelper
        instance). In other words, for each discovery entity, we'll get a queryset of the query executed on the entity
        and count the number of matching entities.
        """

        if self._entity_counts is None:
            async def _get_entity_count(ee: DiscoveryEntity) -> int:
                # We cannot re-validate the field against its options here, as it can trip up "invalid options" due to
                # small cell counts if we're in a nested entity.
                #  => For example, if we have 10 individuals with 2 biosamples after querying, and our field entity is a
                #     biosample but our query is on an individual, we may get a small cell count issue through biosample
                #     but not if we're going through individual (we may have five FEMALE individuals, but only one with
                #     a biosample).
                #
                # We access [0] of the result of get_query_queryset_and_queried_entities because it returns a tuple of
                # (queryset, frozenset of queried entities), but we only need the former (to get the count).
                return await (await self.get_query_queryset_and_queried_entities(ee, validate_field=False))[0].acount()

            self._entity_counts = {
                e: ec
                for e, ec in zip(
                    DISCOVERY_ENTITIES,
                    await asyncio.gather(*(_get_entity_count(e) for e in DISCOVERY_ENTITIES)),
                )
            }

        return self._entity_counts

    @overload
    async def get_censored_entity_counts(self, return_raw_counts: Literal[False] = False) -> EntityCountOrBoolResponse:
        ...

    @overload
    async def get_censored_entity_counts(
        self, return_raw_counts: Literal[True]
    ) -> tuple[EntityCounts, EntityCountOrBoolResponse]:
        ...

    async def get_censored_entity_counts(
        self, return_raw_counts: bool = False,
    ) -> EntityCountOrBoolResponse | tuple[EntityCounts, EntityCountOrBoolResponse]:
        """
        Get censored entity counts for a scope with given permissions, i.e., a given QueryHelper instance.

        This is the shared implementation used by both:
        - Discovery endpoint (with query filters)
        - Project/Dataset serializers (without query filters)

        For each 'discovery entity', we generate either:
         - a count (0/count-if-above-threshold), or
         - a boolean (count > threshold)

        If phenopacket is 0, don't reveal nested entities exist, otherwise we could get responses like (in the case of
        one phenopacket with five biosamples): { phenopacket: 0, biosample: 5, ... }
        ==> do this, plus the same thing for all entities nested inside other entities
            (phenopacket -> biosample -> experiment -> experiment_result...)
        TODO: in the future, if we have other options for non-Phenopackets-centric perspectives, this should instead be
         done in a more dynamic way, starting from the queryset entity.

        Args:
            return_raw_counts: If True, return tuple of (raw_counts, censored_counts) for logging

        Returns:
            If return_raw_counts=False: Dictionary mapping entities to censored counts (int) or booleans
            If return_raw_counts=True: Tuple of (raw counts dict, censored counts dict)
        """

        counts = await self._get_entity_counts()  # cached if already called once here
        censored = await censor_entity_counts(self._scope, counts, self._dt_permissions, self._logger)

        if return_raw_counts:
            return counts, censored

        return censored

    async def get_scope_entities_with_data(self) -> frozenset[DiscoveryEntity]:
        """
        Gets all discovery entities with data in the current scope, ignoring the query. This helps the logic for
        "queried entities" with full-text search (FTS), since entities that aren't present in the current scope should
        not be listed as being queried by the FTS process.
        """

        if self._scope_entities_with_data is None:
            if self._query.is_empty():
                counts = await self.get_censored_entity_counts()
            else:
                qh = QueryHelper(EMPTY_DISCOVERY_QUERY, self.scope, self.dt_permissions, self._logger)
                counts = await qh.get_censored_entity_counts()
            self._scope_entities_with_data = frozenset((e for e, v in counts.items() if v))

        return self._scope_entities_with_data


def get_accepted_formats(request: DrfRequest) -> AcceptedDiscoveryResponseFormats:
    # use these rather than the negotiated renderer, which lets the endpoint return according to _format as well
    # (in the case of discovery matches)

    fmts: set[DiscoveryResponseFormat] = set()

    # noinspection PyProtectedMember
    if request._request.accepts("application/json"):
        fmts.add("json")

    # noinspection PyProtectedMember
    if request._request.accepts("text/csv"):
        fmts.add("csv")

    return frozenset(fmts)


def inject_discovery_deps(empty_404: bool, empty_response: Literal["fields", "data"] = "data"):
    """
    Decorator to inject common discovery dependencies into the discovery API endpoint functions and perform a bit of
    initial setup.

    Args:
        empty_404: specifies whether an empty discovery config means we should return a 404 error (endpoint-dependent).
        empty_response: which empty response to return if discovery config is empty (fields or data).
    """
    def wrapper(
        func: Callable[[DrfRequest, ValidatedDiscoveryScope, DataTypeDiscoveryPermissions, BoundLogger], Awaitable[Any]]
    ):
        @wraps(func)
        async def wrapped(request: DrfRequest):  # wraps a DRF API view
            # for returning error messages
            accepted_formats: AcceptedDiscoveryResponseFormats = get_accepted_formats(request)

            # Get the request discovery scope, which can be used for, e.g., narrowing down the project/dataset for
            # discovery charts/filtering.
            try:
                scope = await get_request_discovery_scope(request)
            except DiscoveryScopeException as e:
                return dres.csv_or_json_error_response(request, errors.not_found_error(e.message), accepted_formats)

            if empty_404 and empty_discovery(scope):
                # If the discovery object is "empty", i.e., no fields/charts/filters specified, this endpoint becomes a
                # 404, here meaning no data could be found for discovery purposes.
                return (
                    dres.no_public_fields(request, accepted_formats)
                    if empty_response == "fields"
                    else dres.no_public_data(request, accepted_formats)
                )

            # Bind scope representation to logger
            lg = logger.bind(scope_repr=repr(scope))

            dt_permissions = await get_discovery_data_type_permissions(request, scope)

            return await func(request, scope, dt_permissions, lg)

        return wrapped

    return wrapper


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
@inject_discovery_deps(empty_404=True, empty_response="fields")
async def discovery_search_fields(
    _request: DrfRequest, scope: ValidatedDiscoveryScope, dt_permissions: DataTypeDiscoveryPermissions, _lg: BoundLogger
):
    """
    get:
    Return discovery search fields with their configuration
    """

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
    qh: QueryHelper,
    field: str,
    censored_counts: EntityCountOrBoolResponse,
    lg: BoundLogger,
) -> DiscoveryFieldResponse | None:
    lg = lg.bind(field=field)

    scope = qh.scope

    field_props = scope.discovery.fields[field]
    field_entity, field_entity_path = normalize_field_path_true_model(*field_props.get_entity_and_field_path())
    field_perms: DataPermissions = qh.dt_permissions[DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE[field_entity]]

    if not field_perms.counts:
        # We cannot compute stats right now for boolean-level responses. Thus, if we do not have at least counts
        # permissions, we return None and this presumably gets filtered out, resulting in this field response not
        # being present in the discovery response. Then, it's up to the API consumer (e.g., the front end) to handle
        # this with relative grace (not show a chart/search field, ...).
        return None

    if not censored_counts[field_entity] and not field_perms.data:
        # We can have counts above the threshold for the field entity that then must get censored because a parent
        # entity is being censored due to low counts. For example, with # phenopackets = 3 and # biosamples = 7, the
        # latter clears the censorship threshold but indirectly reveals the presence of phenopackets, so they both must
        # be censored to 0/False.
        # Of course, if we have the query:data permission for the field, we can safely reveal the true count.
        return None

    # We cannot re-validate the field against its options here, as it can trip up "invalid options" due to small cell
    # counts if we're in a nested entity.
    #  => For example, if we have 10 individuals with 2 biosamples after querying, and our field entity is a
    #     biosample but our query is on an individual, we may get a small cell count issue through biosample but not if
    #     we're going through individual (we may have five FEMALE individuals, but only one with a biosample).
    queryset, _ = await qh.get_query_queryset_and_queried_entities(field_entity, lg, validate_field=False)

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


@api_view(["GET"])
@permission_classes([BentoDeferToHandler])
@inject_discovery_deps(empty_404=True)
async def discovery_endpoint(
    request: DrfRequest, scope: ValidatedDiscoveryScope, dt_permissions: DataTypeDiscoveryPermissions, lg: BoundLogger
):
    """
    get:
    Overview, optionally filtered by fields, of phenopackets+experiments data.
    """

    if not any(d.bool_ for d in dt_permissions.values()):
        # At minimum, we need some bool permissions for data types in order to view True/False for having a specific
        # entity above the count threshold.
        return dres.insufficient_privileges(request)
    authz_middleware.mark_authz_done(request)

    # -- Query execution -----------------------------------------------------------------------------------------------

    # Above, we checked for at minimum one boolean permission for data, since we can skip returning any counts data for
    # fields where we do not have permissions, relying on the front end/API consumer to handle this case.
    # HOWEVER, if we're doing any querying, we will end up needing at least boolean permissions for ALL FIELDS (i.e.,
    # their respective DATA TYPES) queried. Thus, if we're querying, the above check IS NOT SUFFICIENT!
    #  --> this actual second permissions check happens inside the following function stack right now, and raises a
    #      ValidationError:
    #        QueryHelper
    #         --> _execute_discovery_query
    #         --> discovery_filter_queryset
    #         --> the overall_permissions.bool_ check

    queryset_entity: DiscoveryEntity = "phenopacket"

    try:
        query = DiscoveryQuery.from_drf_request(request)
        lg = lg.bind(queried_entity=queryset_entity, query=query.model_dump(mode="json"))
        qh = QueryHelper(query, scope, dt_permissions, lg)
        queryset, queried_entities = await qh.get_query_queryset_and_queried_entities(queryset_entity)
        censored_counts = await qh.get_censored_entity_counts()  # to be used for censoring field responses!
    except ValidationError as e:
        return await dres.django_validation_error(request, e, lg, "discovery endpoint encountered validation error")

    # -- Field responses -----------------------------------------------------------------------------------------------

    discovery = scope.discovery
    fields: tuple[str, ...] = discovery.get_chart_field_ids()

    field_responses: DiscoveryFieldResponses = DiscoveryFieldResponses.model_validate({
        field: field_res
        for field, field_res in zip(
            fields,
            await asyncio.gather(*(discovery_field_response(qh, field, censored_counts, lg) for field in fields))
        )
        if field_res is not None
        # Parallel async collection of field responses for public overview
    })

    # -- Counts processing ---------------------------------------------------------------------------------------------

    message: str = ""

    # Get both raw counts (for logging) and censored counts (for response)
    # Uses the same shared implementation as Project/Dataset serializers
    counts, count_or_bools_res = await qh.get_censored_entity_counts(return_raw_counts=True)

    if (
        not count_or_bools_res[queryset_entity]
        and not dt_permissions[DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE[queryset_entity]].data
    ):
        message = dres.INSUFFICIENT_DATA_AVAILABLE_MSG

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
@renderer_classes([JSONRenderer, PassThruCSVRenderer])  # renderers here are just handling negotiation
@inject_discovery_deps(empty_404=True)
async def discovery_matches(
    request: DrfRequest, scope: ValidatedDiscoveryScope, dt_permissions: DataTypeDiscoveryPermissions, lg: BoundLogger
):
    """
    Returns a paginated result-set of entity matches for a discovery query. For a given query, this endpoint can return
    different entities at the top-level using the _entity parameter.

    Query parameters:
      /^[^_].*$/: Discovery field filters, like discovery_endpoint above
      _fts:       Full-text search (FTS) query
      _fts_type:  FTS query type (from Django, see DiscoveryQuery model for more information). Default: 'plain'.
      _entity:    Entity to return in result-set. phenopacket|individual|biosample|experiment|experiment_result
      _page:      Page number, 0-indexed integer; defaults to 0
      _page_size: Page size; defaults to 25
      _format:    Response format ("json" or "csv"; must match request Accept header[s])
      project:    Discovery scope - project ID (if not set, the global scope is used)
      dataset:    Discovery scope - dataset ID (if not set, the project or global scope is used)

    Note on query parameter names:
      - QueryHelper._execute_discovery_query calls build_discovery_query_from_request, which grabs every query
        parameter except "project", "dataset", and those starting with "_" and tries to find fields to query.
        By separating the namespace for discovery filter query parameters from "other" query parameters by prefixing
        other query parameters with _, we eliminate possible ambiguities between discovery fields.

    Links for full-text search type:
      - https://docs.djangoproject.com/en/5.2/ref/contrib/postgres/search/#searchquery
      - https://www.postgresql.org/docs/18/textsearch-controls.html#TEXTSEARCH-PARSING-QUERIES
    """

    # -- Response format -----------------------------------------------------------------------------------------------

    accepted_formats: AcceptedDiscoveryResponseFormats = get_accepted_formats(request)

    response_format_param: str = request.query_params.get("_format", "")

    if not response_format_param:
        if "json" in accepted_formats:
            # default response format: JSON
            response_format_param = "json"
        elif "csv" in accepted_formats:
            # if we can accept CSV but not JSON and _format is not set --> response format should be CSV
            response_format_param = "csv"

    if response_format_param not in ("json", "csv"):
        return dres.csv_or_json_error_response(
            request, errors.bad_request_error("bad response format"), accepted_formats
        )

    # we've now validated these values so this can be coerced to the DiscoveryResponseFormat Literal type
    response_format: DiscoveryResponseFormat = response_format_param

    # noinspection PyProtectedMember
    if response_format not in accepted_formats:
        return dres.csv_or_json_error_response(
            request,
            errors.not_acceptable_error("mismatch between accepted and specified response formats"),
            accepted_formats,
        )

    lg = lg.bind(response_format=response_format)

    # -- Queried entity: grab from query parameters + validate ---------------------------------------------------------

    queried_entity: DiscoveryEntity = request.query_params.get("_entity", "phenopacket")
    if queried_entity not in DISCOVERY_ENTITIES:
        return dres.csv_or_json_error_response(request, errors.bad_request_error("invalid entity"), accepted_formats)

    lg = lg.bind(queried_entity=queried_entity)

    # -- Permissions check ---------------------------------------------------------------------------------------------

    if not dt_permissions[DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE[queried_entity]].data:
        # "Extra" permissions check vs. regular discovery endpoint: we need full data permissions
        # Since we require query:data here, we don't need to be vigilant about censoring below
        return dres.insufficient_privileges(request, accepted_formats)

    authz_middleware.mark_authz_done(request)

    # -- Query execution -----------------------------------------------------------------------------------------------

    try:
        query = DiscoveryQuery.from_drf_request(request)
        qh = QueryHelper(query, scope, dt_permissions, lg)
        queryset, _ = await qh.get_query_queryset_and_queried_entities(queried_entity)
        # queryset = queryset.order_by("pk")
    except ValidationError as e:
        return await dres.django_validation_error(
            request, e, lg, "discovery matches endpoint encountered validation error", accepted_formats
        )

    lg = lg.bind(query=query.model_dump(mode="json"))

    # -- Pagination ----------------------------------------------------------------------------------------------------

    page: int = 0
    page_size: int = DEFAULT_PAGE_SIZE

    try:
        page: int = int(request.query_params.get("_page", str(page)))
    except ValueError:
        return dres.csv_or_json_error_response(request, errors.bad_request_error("bad page"), accepted_formats)

    try:
        # if page_size is set to 0, all records will be returned.
        # if page_size is less than 0, it will be set to 0; if it is greater than DEFAULT_MAX_PAGE_SIZE, it'll be set
        #  to that value.
        page_size = min(max(int(request.query_params.get("_page_size", str(page_size))), 0), DEFAULT_MAX_PAGE_SIZE)
    except ValueError:
        return dres.csv_or_json_error_response(request, errors.bad_request_error("bad page size"), accepted_formats)

    total_count = await queryset.acount()

    if page < 0 or (page_size and total_count and page >= math.ceil(total_count / page_size)):
        return dres.csv_or_json_error_response(request, errors.bad_request_error("bad page"), accepted_formats)

    pagination = DiscoveryPagination(page=page, page_size=page_size, total=total_count)
    lg = lg.bind(pagination=pagination.model_dump(mode="json"))

    matches_page: QuerySet
    if page_size > 0:
        matches_page = queryset[page * page_size:(page + 1) * page_size] if page_size > 0 else queryset[:]
    else:
        matches_page = queryset[:]

    # -- Log discovery match page fetch event --------------------------------------------------------------------------

    # structured event logging for discovery: embed search details
    await lg.ainfo("discovery matches requested")

    # -- Build and return response -------------------------------------------------------------------------------------

    if response_format == "csv":
        @sync_to_async
        def _get_csv():
            renderer = DISCOVERY_ENTITY_TO_CSV_RENDERER[queried_entity]()
            return renderer.render(renderer.get_model_serializer()(matches_page, many=True).data)

        return await _get_csv()

    # Otherwise, return a CSV response
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
@inject_discovery_deps(empty_404=True)
async def discovery_ui_hints(
    _request: DrfRequest, scope: ValidatedDiscoveryScope, dt_permissions: DataTypeDiscoveryPermissions, lg: BoundLogger
):
    """
    Endpoint for returning miscellaneous UI hints for any front-end which consumes the various discovery endpoints.
    For example:
     - indications of which elements should be hidden in the front end, to avoid a bunch of ugly disabled elements for
       projects/datasets which don't have any intention of ingesting, e.g., experiment data or geographical data.
     - indications of the presence of certain types of data, e.g1., geographical data, to encourage API consumers to
       render a certain element (e.g., a map).
    """

    # TODO: support querying?
    qh = QueryHelper(EMPTY_DISCOVERY_QUERY, scope, dt_permissions, lg)
    entities_with_data = await qh.get_scope_entities_with_data()

    return Response(DiscoveryUIHintsResponse(
        # This helps the UI determine which entities are available in a particular scope, so we can hide entities with
        # no data ingested (e.g., not showing experiments for an instance with only phenopackets). Because of this
        # purpose, we don't filter it beforehand - we still want to see 0 counts if they're the result of a specific
        # search, but we don't want them
        entities_with_data=entities_with_data,
        # TODO: implement something like this for hinting towards maps
        # TODO: instead of this, maybe we also collect experiment results and check for geojson, and indicate if we
        #  should present a consolidated map view?
        # "biosample_location_present": False,  # TODO: non-Null location_collected above threshold
    ))


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
@inject_discovery_deps(empty_404=False)
async def discovery_rules(
    _request: DrfRequest, scope: ValidatedDiscoveryScope, dt_permissions: DataTypeDiscoveryPermissions, _lg: BoundLogger
):
    """
    Endpoint for censorship / display rules (count threshold, maximum query parameters).
    Returns a serialization of the DiscoveryConfigRules object from bento_lib.discovery.models.config
    """

    # TODO: allow filtering by fields accessed?
    fs_permissions, _ = get_discovery_field_set_permissions(scope, None, dt_permissions)

    return Response(get_rules(scope, data_permissions=fs_permissions), status=status.HTTP_200_OK)
