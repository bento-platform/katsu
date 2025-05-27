import asyncio

from adrf.decorators import api_view
from bento_lib.discovery import SearchSection, DiscoveryEntity
from bento_lib.responses import errors
from chord_metadata_service.patients.models import Individual
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema, inline_serializer
from functools import partial
from operator import is_not
from rest_framework import serializers, status
from rest_framework.decorators import permission_classes
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response
from typing import Type

from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.authz.permissions import BentoAllowAny
from chord_metadata_service.authz.types import DataPermissions
from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope
from chord_metadata_service.discovery.utils import empty_discovery
from chord_metadata_service.logger import logger

from . import responses as dres
from .censorship import get_rules, get_threshold
from .exceptions import DiscoveryEmptyException, DiscoveryScopeException
from .fields import get_field_options, get_range_stats, get_categorical_stats, get_date_stats
from .filtering import build_discovery_query_from_request, discovery_filter_queryset
from .model_lookups import DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE, DISCOVERY_ENTITY_NAMES_TO_MODEL
from .pydantic_models import (
    DiscoveryFieldResponse,
    DiscoveryFieldResponses,
    DiscoveryResponse,
    BinList,
    DiscoveryFieldAndOptions,
    DiscoverySearchSectionWithOptions,
    DiscoverySearchFieldsResponse,
)
from .schemas import DISCOVERY_SCHEMA
from .scope import get_request_discovery_scope
from .scopeable_model import BaseScopeableModel
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
        discovery_scope: ValidatedDiscoveryScope = await get_request_discovery_scope(request)
    except DiscoveryScopeException as e:
        return Response(errors.not_found_error(e.message), status=status.HTTP_404_NOT_FOUND)

    if empty_discovery(discovery_scope):
        return Response(dres.NO_PUBLIC_FIELDS_CONFIGURED, status=status.HTTP_404_NOT_FOUND)

    dt_permissions = await get_discovery_data_type_permissions(request, discovery_scope)

    discovery = discovery_scope.discovery
    _, field_permissions = get_discovery_field_set_permissions(discovery, None, dt_permissions)

    # ------------------------------------------------------------------------------------------------------------------

    queryset_model_name: DiscoveryEntity = "phenopacket"
    queryset = DISCOVERY_ENTITY_NAMES_TO_MODEL[queryset_model_name].get_model_scoped_queryset(discovery_scope)

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
            options=await get_field_options(
                queryset_model_name,
                queryset,
                field,
                discovery_scope,
                field_permissions[field],
            )
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
    discovery_scope: ValidatedDiscoveryScope,
    queryset_model_name: DiscoveryEntity,
    queryset: QuerySet,
    field: str,
    field_perms: DataPermissions,
) -> DiscoveryFieldResponse | None:
    field_props = discovery_scope.discovery.fields[field]

    stats: BinList

    if not field_perms.counts:
        return None  # cannot compute stats right now for boolean-level responses
    if field_props.datatype == "string":
        stats = await get_categorical_stats(
            discovery_scope, queryset_model_name, queryset, field_props.root, field_perms
        )
    elif field_props.datatype == "number":
        stats = await get_range_stats(discovery_scope, queryset_model_name, queryset, field_props.root, field_perms)
    elif field_props.datatype == "date":
        stats = await get_date_stats(discovery_scope, queryset_model_name, queryset, field_props.root, field_perms)
    else:  # pragma: no cover
        # Can't actually occur with Pydantic implementation of the discovery configuration model, which will
        # validate the data_type value.
        raise NotImplementedError()

    return DiscoveryFieldResponse(id=field, definition=field_props, data=stats)


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
        discovery_scope = await get_request_discovery_scope(request)
    except DiscoveryScopeException as e:
        return Response(errors.not_found_error(e.message), status=status.HTTP_404_NOT_FOUND)

    # If the discovery object is "empty", i.e., no fields/charts/filters specified, this endpoint becomes a 404, here
    # meaning no data could be found for discovery purposes.
    if empty_discovery(discovery_scope):
        return Response(dres.NO_PUBLIC_DATA_AVAILABLE, status=status.HTTP_404_NOT_FOUND)

    dt_permissions = await get_discovery_data_type_permissions(request, discovery_scope)
    if not any(d.counts for d in dt_permissions.values()):
        return Response(dres.INSUFFICIENT_PRIVILEGES, status=status.HTTP_403_FORBIDDEN)

    # ------------------------------------------------------------------------------------------------------------------

    # TODO: support free text search as well as filters query

    query = build_discovery_query_from_request(request)
    queryset_model_name: DiscoveryEntity = "phenopacket"
    queryset = DISCOVERY_ENTITY_NAMES_TO_MODEL[queryset_model_name].get_model_scoped_queryset(discovery_scope)

    # ------------------------------------------------------------------------------------------------------------------

    try:
        queryset = await discovery_filter_queryset(
            discovery_scope, query, queryset_model_name, queryset, dt_permissions, logger
        )
    except DiscoveryEmptyException:
        authz_middleware.mark_authz_done(request)
        return Response(dres.NO_PUBLIC_DATA_AVAILABLE, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        await logger.ainfo(
            "discovery endpoint recieved validation error", exc=e, scope_repr=repr(discovery_scope)
        )
        authz_middleware.mark_authz_done(request)
        return Response(errors.bad_request_error(
            *(e.error_list if hasattr(e, "error_list") else e.error_dict.items()),
        ), status=status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------------------------------------------------------

    discovery = discovery_scope.discovery
    fields: tuple[str, ...] = discovery.get_chart_field_ids()
    _, field_permissions = get_discovery_field_set_permissions(discovery, fields, dt_permissions)

    field_responses: DiscoveryFieldResponses = DiscoveryFieldResponses.model_validate({
        field: field_res
        for field, field_res in zip(
            fields,
            await asyncio.gather(
                *(
                    discovery_field_response(
                        discovery_scope, queryset_model_name, queryset, field, field_permissions[field]
                    )
                    for field in fields
                )
            )
        )
        if field_res is not None
        # Parallel async collection of field responses for public overview
    })

    # TODO: log

    # ------------------------------------------------------------------------------------------------------------------

    # for each 'discovery entity', we generate either:
    #  - a count (0/count-if-above-threshold), or
    #  - a boolean (count > threshold)

    # TODO: permissions non-hard-coded
    # TODO: do this in sql instead
    counts: dict[DiscoveryEntity, int] = {
        "phenopacket": await queryset.acount(),
        "individual": 0,
        "biosample": 0,
        "experiment": 0,
    }

    async for p in queryset:
        counts["individual"] += (1 if p.subject_id is not None else 0)
        counts["biosample"] += p.count_biosample
        counts["experiment"] += p.count_experiment

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
            await logger.ainfo(
                "discovery: entity count is below threshold",
                entity=e,
                threshold=count_threshold,
                scope_repr=repr(discovery_scope),
            )
            entity_count = 0  # censor sub-threshold counts to 0

        if entity_permissions.any_permissions():  # if we have any permissions, then add a response for the overview
            # if we only have boolean permissions, store a Boolean "count" (yes or no to above-threshold count) if we
            # didn't get censored down to 0 above.
            # This key used to be a plural version of the public model name, but is now singular so we have a consistent
            # key to use across all discovery endpoints:
            count_or_bools_res[e] = entity_count if entity_permissions.counts else (entity_count > 0)

    # ------------------------------------------------------------------------------------------------------------------

    return Response(
        DiscoveryResponse(
            layout=discovery.overview,
            fields=field_responses,
            root_entity=queryset_model_name,
            # permissions-dependent: dictionary of {entity: counts or True if above threshold, 0/False otherwise}:
            counts=count_or_bools_res,
            # if we have full data access, we have matches as well:
            matches=None,  # TODO !!!!
        )
    )


@extend_schema(
    description="Overview of all public data in the database",
    responses={
        status.HTTP_200_OK: inline_serializer(
            name='public_overview_response',
            fields={'datasets': serializers.CharField()}
        ),
        status.HTTP_404_NOT_FOUND: inline_serializer(
            name='public_overview_not_available',
            fields={'message': serializers.CharField()},
        ),
    }
)
@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def public_overview(request: DrfRequest):
    """
    get:
    Overview of all public data in the database
    """

    try:
        discovery_scope = await get_request_discovery_scope(request)
    except DiscoveryScopeException as e:
        return Response(errors.not_found_error(e.message), status=status.HTTP_404_NOT_FOUND)

    if empty_discovery(discovery_scope):
        return Response(dres.NO_PUBLIC_DATA_AVAILABLE, status=status.HTTP_404_NOT_FOUND)

    dt_permissions = await get_discovery_data_type_permissions(request, discovery_scope)
    if not any(d.bool_ for d in dt_permissions.values()):
        return Response(dres.INSUFFICIENT_PRIVILEGES, status=status.HTTP_403_FORBIDDEN)

    discovery = discovery_scope.discovery

    async def _counts_for_scoped_model_name(
        m: tuple[DiscoveryEntity, Type[BaseScopeableModel]]
    ) -> tuple[DiscoveryEntity, int]:
        mn, model = m
        return mn, await model.get_model_scoped_queryset(discovery_scope).acount()

    # Predefined counts
    counts: dict[DiscoveryEntity, int] = dict(
        await asyncio.gather(*map(_counts_for_scoped_model_name, DISCOVERY_ENTITY_NAMES_TO_MODEL.items())))

    # for each 'discovery entity', we generate either:
    #  - a count (0/count-if-above-threshold), or
    #  - a boolean (count > threshold)
    count_or_bools_res: dict[DiscoveryEntity, int | bool] = {}

    # Set counts to 0 (or bool to False) if they're under the count threshold and the threshold is positive.
    for public_model_name in counts:
        dt = DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE[public_model_name]
        model_permissions = dt_permissions[dt]
        count_threshold = get_threshold(discovery, model_permissions)

        model_count = counts[public_model_name]

        # Extra check for threshold being above 0 to not log warnings for true-0 counts with query:data
        if 0 < counts[public_model_name] <= count_threshold and count_threshold > 0:
            await logger.ainfo(
                "public overview: model count is below threshold",
                model=public_model_name,
                threshold=count_threshold,
                scope_repr=repr(discovery_scope),
            )
            model_count = 0

        if model_permissions.any_permissions():  # if we have any permissions, then add a response for the overview
            # if we only have boolean permissions, store a Boolean "count" (yes or no to above-threshold count) if we
            # didn't get censored down to 0 above.
            # This key used to be a plural version of the public model name, but is now singular so we have a consistent
            # key to use across all discovery endpoints:
            count_or_bools_res[public_model_name] = model_count if model_permissions.counts else (model_count > 0)

    # Parse the public config to gather data for each field defined in the overview

    fields: tuple[str, ...] = discovery.get_chart_field_ids()
    _, field_permissions = get_discovery_field_set_permissions(discovery, fields, dt_permissions)

    # TODO: exclude field when no permissions or something, right now this isn't handled well
    #  !!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #  !!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #  !!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #  !!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Parse the public config to gather data for each field defined in the overview

    fields = discovery.get_chart_field_ids()
    _, field_permissions = get_discovery_field_set_permissions(discovery, fields, dt_permissions)

    queryset_model_name: DiscoveryEntity = "individual"
    queryset = Individual.get_model_scoped_queryset(discovery_scope)

    field_responses: DiscoveryFieldResponses = DiscoveryFieldResponses.model_validate({
        field: field_res
        for field, field_res in zip(
            fields,
            await asyncio.gather(
                *(
                    discovery_field_response(
                        discovery_scope, queryset_model_name, queryset, field, field_permissions[field]
                    )
                    for field in fields
                )
            )
        )
        if field_res is not None
        # Parallel async collection of field responses for public overview
    })

    return Response(
        DiscoveryResponse(
            layout=discovery.overview,
            fields=field_responses,
            # permissions-dependent: dictionary of {entity: counts or True if above threshold, 0/False otherwise}:
            root_entity=queryset_model_name,
            counts=count_or_bools_res,
        )
    )


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
