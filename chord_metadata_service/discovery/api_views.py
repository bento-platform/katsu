import asyncio

from adrf.decorators import api_view
from bento_lib.discovery import SearchSection, DiscoveryEntity
from bento_lib.responses import errors
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema, inline_serializer
from functools import partial
from operator import is_not
from rest_framework import serializers, status
from rest_framework.decorators import permission_classes
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response

from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.authz.permissions import BentoAllowAny, BentoDeferToHandler
from chord_metadata_service.authz.types import DataPermissions, DataTypeDiscoveryPermissions
from chord_metadata_service.chord import data_types as dts
from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope
from chord_metadata_service.discovery.utils import empty_discovery
from chord_metadata_service.logger import logger

from . import responses as dres
from .censorship import get_rules, get_threshold, thresholded_count
from .exceptions import DiscoveryEmptyException, DiscoveryScopeException
from .fields import get_field_options, get_range_stats, get_categorical_stats, get_date_stats
from .filtering import build_discovery_query_from_request, discovery_filter_queryset
from .matches import DISCOVERY_ENTITY_TO_MATCH_FN
from .model_lookups import DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE, DISCOVERY_ENTITY_NAMES_TO_MODEL
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
from .utils import get_discovery_data_type_permissions, get_discovery_field_set_permissions

is_not_none = partial(is_not, None)


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
        return Response(errors.not_found_error(e.message), status=status.HTTP_404_NOT_FOUND)

    if empty_discovery(scope):
        return Response(dres.NO_PUBLIC_FIELDS_CONFIGURED, status=status.HTTP_404_NOT_FOUND)

    dt_permissions = await get_discovery_data_type_permissions(request, scope)

    discovery = scope.discovery
    _, field_permissions = get_discovery_field_set_permissions(discovery, None, dt_permissions)

    # ------------------------------------------------------------------------------------------------------------------

    queryset_model_name: DiscoveryEntity = "phenopacket"
    queryset = DISCOVERY_ENTITY_NAMES_TO_MODEL[queryset_model_name].get_model_scoped_queryset(scope)

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
            options=await get_field_options(queryset_model_name, queryset, field, scope, field_permissions[field]),
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
    scope: ValidatedDiscoveryScope,
    queryset_model_name: DiscoveryEntity,
    queryset: QuerySet,
    field: str,
    field_perms: DataPermissions,
) -> DiscoveryFieldResponse | None:
    field_props = scope.discovery.fields[field]

    stats: BinList

    if not field_perms.counts:
        return None  # cannot compute stats right now for boolean-level responses
    if field_props.datatype == "string":
        stats = await get_categorical_stats(scope, queryset_model_name, queryset, field_props.root, field_perms)
    elif field_props.datatype == "number":
        stats = await get_range_stats(scope, queryset_model_name, queryset, field_props.root, field_perms)
    elif field_props.datatype == "date":
        stats = await get_date_stats(scope, queryset_model_name, queryset, field_props.root, field_perms)
    else:  # pragma: no cover
        # Can't actually occur with Pydantic implementation of the discovery configuration model, which will
        # validate the data_type value.
        raise NotImplementedError()

    return DiscoveryFieldResponse(id=field, definition=field_props, data=stats)


async def build_and_execute_discovery_query(
    request: DrfRequest,
    discovery_scope: ValidatedDiscoveryScope,
    dt_permissions: DataTypeDiscoveryPermissions,
    queryset_model_name: DiscoveryEntity,
) -> tuple[DiscoveryQuery, QuerySet]:
    # TODO: support free text search as well as filters query

    query = build_discovery_query_from_request(request)

    # May raise:
    #  - DiscoveryEmptyException
    #  - ValidationError
    return query, await discovery_filter_queryset(
        discovery_scope,
        query,
        queryset_model_name,
        DISCOVERY_ENTITY_NAMES_TO_MODEL[queryset_model_name].get_model_scoped_queryset(discovery_scope),
        dt_permissions,
        logger,
    )


async def discovery_queryset_entity_counts(queryset: QuerySet) -> dict[DiscoveryEntity, int]:
    # TODO: do this in sql instead
    # TODO: do this for different base entity types

    counts: dict[DiscoveryEntity, int] = {
        "phenopacket": await queryset.acount(),
        "individual": 0,
        "biosample": 0,
        "experiment": 0,
        "experiment_result": 0,
    }

    async for p in queryset:
        counts["individual"] += (1 if p.subject_id is not None else 0)
        counts["biosample"] += p.count_biosample
        counts["experiment"] += p.count_experiment
        counts["experiment_result"] += p.count_experiment_result

    return counts


@api_view(["GET", "POST"])
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
        return Response(errors.not_found_error(e.message), status=status.HTTP_404_NOT_FOUND)

    lg = logger.bind(scope_repr=repr(scope))

    # If the discovery object is "empty", i.e., no fields/charts/filters specified, this endpoint becomes a 404, here
    # meaning no data could be found for discovery purposes.
    if empty_discovery(scope):
        return dres.no_public_data(request)

    dt_permissions = await get_discovery_data_type_permissions(request, scope)
    if not any(d.counts for d in dt_permissions.values()):
        return dres.insufficient_privileges(request)

    # -- Query execution -----------------------------------------------------------------------------------------------

    queryset_model_name: DiscoveryEntity = "phenopacket"

    try:
        query, queryset = await build_and_execute_discovery_query(request, scope, dt_permissions, queryset_model_name)
    except DiscoveryEmptyException:
        return dres.no_public_data(request)
    except ValidationError as e:
        return await dres.django_validation_error(request, e, lg, "discovery endpoint recieved validation error")

    lg = lg.bind(queried_entity=queryset_model_name, query=query.model_dump(mode="json"))

    # -- Field responses -----------------------------------------------------------------------------------------------

    discovery = scope.discovery
    fields: tuple[str, ...] = discovery.get_chart_field_ids()
    _, field_permissions = get_discovery_field_set_permissions(discovery, fields, dt_permissions)

    field_responses: DiscoveryFieldResponses = DiscoveryFieldResponses.model_validate({
        field: field_res
        for field, field_res in zip(
            fields,
            await asyncio.gather(
                *(
                    discovery_field_response(scope, queryset_model_name, queryset, field, field_permissions[field])
                    for field in fields
                )
            )
        )
        if field_res is not None
        # Parallel async collection of field responses for public overview
    })

    # -- Counts processing ---------------------------------------------------------------------------------------------

    message: str = ""

    # for each 'discovery entity', we generate either:
    #  - a count (0/count-if-above-threshold), or
    #  - a boolean (count > threshold)

    # TODO: permissions non-hard-coded
    # TODO: do this in sql instead
    counts: dict[DiscoveryEntity, int] = await discovery_queryset_entity_counts(queryset)

    # for each 'discovery entity', we generate either:
    #  - a count (0/count-if-above-threshold), or
    #  - a boolean (count > threshold)
    count_or_bools_res: dict[DiscoveryEntity, int | bool] = {}

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
        not count_or_bools_res[queryset_model_name]
        and not dt_permissions[DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE[queryset_model_name]].data
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
            root_entity=queryset_model_name,
            message=message,
            # permissions-dependent: dictionary of {entity: counts or True if above threshold, 0/False otherwise}:
            counts=count_or_bools_res,
        )
    )


@api_view(["GET", "POST"])
@permission_classes([BentoDeferToHandler])
async def discovery_matches(request: DrfRequest):
    # TODO: DEDUPLICATE

    # Get the request discovery scope, which we'll use to narrow down the project/dataset for discovery
    # charts/filtering.
    try:
        scope = await get_request_discovery_scope(request)
    except DiscoveryScopeException as e:
        authz_middleware.mark_authz_done(request)
        return Response(errors.not_found_error(e.message), status=status.HTTP_404_NOT_FOUND)

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

    queryset_model_name: DiscoveryEntity = "phenopacket"

    try:
        query, queryset = await build_and_execute_discovery_query(request, scope, dt_permissions, queryset_model_name)
    except DiscoveryEmptyException:
        return dres.no_public_data(request)
    except ValidationError as e:
        return await dres.django_validation_error(
            request, e, lg, "discovery matches endpoint recieved validation error"
        )

    lg = lg.bind(query=query.model_dump(mode="json"))

    # -- Pagination ----------------------------------------------------------------------------------------------------

    page: int = int(request.query_params.get("_page", "0"))
    page_size = int(request.query_params.get("_page_size", "10"))  # if page_size is set to 0,
    total_count = await queryset.acount()

    if page_size > 0:
        matches_page = queryset[page * page_size:(page + 1) * page_size]
    else:
        matches_page = queryset[:]

    pagination = DiscoveryPagination(page=page, page_size=page_size, total=total_count)

    lg = lg.bind(pagination=pagination.model_dump(mode="json"))

    # -- Log discovery match page fetch event --------------------------------------------------------------------------

    # structured event logging for discovery: embed search details
    await lg.ainfo("discovery matches requested")

    # -- Build and return response -------------------------------------------------------------------------------------

    results_entity: DiscoveryEntity = "phenopacket"
    # TODO: select queryset of entities that aren't necessarily phenopackets

    return Response(
        DiscoveryMatchesPaginatedResponse(
            results_entity=results_entity,
            results=DiscoveryMatches(
                root=await DISCOVERY_ENTITY_TO_MATCH_FN[results_entity](matches_page, scope, dt_permissions, True, {})
            ),
            pagination=pagination,
        ).model_dump(mode="json", exclude_unset=True)
    )


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def discovery_ui_hints(request: DrfRequest):
    try:
        scope = await get_request_discovery_scope(request)
    except DiscoveryScopeException as e:
        return Response(errors.not_found_error(e.message), status=status.HTTP_404_NOT_FOUND)

    queryset_model_name: DiscoveryEntity = "phenopacket"  # TODO
    queryset = DISCOVERY_ENTITY_NAMES_TO_MODEL[queryset_model_name].get_model_scoped_queryset(scope)

    counts = await discovery_queryset_entity_counts(queryset=queryset)

    dt_permissions = await get_discovery_data_type_permissions(request, scope)

    return {
        "entities_with_data": [
            e for e, v in counts.items()
            if thresholded_count(v, scope, dt_permissions[DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE[e]])
        ],
        # TODO: instead of this, maybe we also collect experiment results and check for geojson, and indicate if we
        #  should present a consolidated map view?
        "biosample_location_present": False,  # TODO: non-Null location_collected above threshold
    }


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def discovery_schema(_request: DrfRequest):
    return Response(DISCOVERY_SCHEMA)


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def public_rules(request: DrfRequest):
    try:
        discovery_scope = await get_request_discovery_scope(request)
    except DiscoveryScopeException as e:
        return Response(e.message, status=status.HTTP_404_NOT_FOUND)

    dt_permissions = await get_discovery_data_type_permissions(request, discovery_scope)

    # TODO: allow filtering by fields accessed?
    fs_permissions, _ = get_discovery_field_set_permissions(discovery_scope, None, dt_permissions)

    return Response(get_rules(discovery_scope, data_permissions=fs_permissions), status=status.HTTP_200_OK)
