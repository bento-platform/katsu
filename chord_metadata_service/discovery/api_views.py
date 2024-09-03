import asyncio

from adrf.decorators import api_view
from bento_lib.responses import errors
from django.conf import settings
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import permission_classes
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response

from chord_metadata_service.discovery.exceptions import DiscoveryScopeException
from chord_metadata_service.discovery.utils import get_request_discovery_scope

from ..authz.permissions import BentoAllowAny
from ..chord import data_types as dts, models as cm
from ..logger import logger

from .fields import get_field_options, get_range_stats, get_categorical_stats, get_date_stats
from .model_lookups import (
    PUBLIC_MODEL_NAMES_TO_DATA_TYPE,
    PUBLIC_MODEL_NAMES_TO_MODEL,
    PUBLIC_MODEL_NAMES_TO_SCOPE_FILTERS,
    PublicModelNames,
    PublicScopeFilterKeys,
)
from . import responses as dres
from .censorship import get_rules
from .schemas import DISCOVERY_SCHEMA
from .types import BinWithValue
from .utils import get_discovery_data_type_permissions, get_discovery_field_set_permissions


@extend_schema(
    description="Public search fields with their configuration",
    responses={
        status.HTTP_200_OK: inline_serializer(
            name='public_search_fields_response',
            fields={'sections': serializers.JSONField()}
        ),
        status.HTTP_404_NOT_FOUND: inline_serializer(
            name='public_search_fields_not_configured',
            fields={'message': serializers.CharField()},
        ),
    }
)
@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def public_search_fields(request: DrfRequest):
    """
    get:
    Return public search fields with their configuration
    """

    try:
        discovery_scope = await get_request_discovery_scope(request)
    except DiscoveryScopeException as e:
        return Response(e.message, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:  # UUID error
        return Response(errors.bad_request_error(*e.messages), status=status.HTTP_400_BAD_REQUEST)

    discovery = await discovery_scope.get_discovery()

    if not discovery:
        return Response(dres.NO_PUBLIC_FIELDS_CONFIGURED, status=status.HTTP_404_NOT_FOUND)

    dt_permissions = await get_discovery_data_type_permissions(request, discovery_scope)
    _, field_permissions = get_discovery_field_set_permissions(discovery, None, dt_permissions)

    # Note: the array is wrapped in a dictionary structure to help with JSON
    # processing by some services.

    async def _get_field_response(field) -> dict | None:
        field_props = discovery.get("fields", {}).get(field, {})
        field_perms = field_permissions[field]

        if not field_perms["counts"]:  # Cannot even see counts, skip this field  TODO: incorporate booleans
            return None

        return {
            **field_props,
            "id": field,
            "options": await get_field_options(field, discovery, field_permissions[field]),
        }

    async def _get_section_response(section) -> dict:
        return {
            **section,
            "fields": await asyncio.gather(*filter(None, map(_get_field_response, section["fields"]))),
        }

    return Response({
        "sections": await asyncio.gather(*map(_get_section_response, discovery["search"])),
    })


async def _counts_for_model_name(mn: PublicModelNames) -> tuple[PublicModelNames, int]:
    return mn, await PUBLIC_MODEL_NAMES_TO_MODEL[mn].objects.all().acount()


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
        return Response(e.message, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        return Response(errors.bad_request_error(*e.messages), status=status.HTTP_400_BAD_REQUEST)

    discovery = await discovery_scope.get_discovery()

    if not discovery:
        return Response(dres.NO_PUBLIC_DATA_AVAILABLE, status=status.HTTP_404_NOT_FOUND)

    dt_permissions = await get_discovery_data_type_permissions(request, discovery_scope)
    if not any(d["counts"] for d in dt_permissions.values()):
        return Response(dres.INSUFFICIENT_PRIVILEGES, status=status.HTTP_403_FORBIDDEN)

    project_id = discovery_scope.project_id
    dataset_id = discovery_scope.dataset_id

    async def _counts_for_scoped_model_name(mn: PublicModelNames) -> tuple[PublicModelNames, int]:
        scope: PublicScopeFilterKeys
        if dataset_id:
            scope = "dataset"
            value = dataset_id
        elif project_id and not dataset_id:
            scope = "project"
            value = project_id
        else:
            return await _counts_for_model_name(mn)

        filter_query = PUBLIC_MODEL_NAMES_TO_SCOPE_FILTERS[mn][scope]["filter"]
        prefetch = PUBLIC_MODEL_NAMES_TO_SCOPE_FILTERS[mn][scope]["prefetch_related"]

        return mn, await PUBLIC_MODEL_NAMES_TO_MODEL[mn].objects.prefetch_related(*prefetch).filter(
            **{filter_query: value}
        ).acount()

    # Predefined counts
    counts = dict(await asyncio.gather(*map(_counts_for_scoped_model_name, PUBLIC_MODEL_NAMES_TO_MODEL)))

    # Set counts to 0 if they're under the count threshold and the threshold is positive.
    for public_model_name in counts:
        dt = PUBLIC_MODEL_NAMES_TO_DATA_TYPE[public_model_name]
        rules = get_rules(discovery, dt_permissions[dt])
        count_threshold = rules["count_threshold"]

        # Extra check for threshold being above 0 to not log warnings for true-0 counts with query:data
        if 0 < counts[public_model_name] <= count_threshold and count_threshold > 0:
            logger.info(
                f"Public overview: {public_model_name} count is below count threshold of {count_threshold} "
                f"(project={project_id}, dataset={dataset_id})"
            )
            counts[public_model_name] = 0

    response = {
        "layout": discovery["overview"],
        "fields": {},
        "counts": {
            **({
                "individuals": counts["individual"],
                "biosamples": counts["biosample"],
            } if dt_permissions[dts.DATA_TYPE_PHENOPACKET]["counts"] else {}),
            **({
                "experiments": counts["experiment"],
            } if dt_permissions[dts.DATA_TYPE_EXPERIMENT]["counts"] else {}),
        },
    }

    # Parse the public config to gather data for each field defined in the overview

    fields = [chart["field"] for section in discovery["overview"] for chart in section["charts"]]
    field_conf = discovery["fields"]

    _, field_permissions = get_discovery_field_set_permissions(discovery, fields, dt_permissions)

    async def _get_field_response(field: str) -> dict:
        field_props = field_conf.get(field, {"datatype": None})
        field_perms = field_permissions[field]

        stats: list[BinWithValue] | None
        if field_props["datatype"] == "string":
            stats = await get_categorical_stats(field, discovery, field_perms, project_id, dataset_id)
        elif field_props["datatype"] == "number":
            stats = await get_range_stats(field, discovery, field_perms, project_id, dataset_id)
        elif field_props["datatype"] == "date":
            stats = await get_date_stats(field, discovery, field_perms, project_id, dataset_id)
        else:
            raise NotImplementedError()

        return {
            **field_props,
            "id": field,
            **({"data": stats} if stats is not None else {}),
        }

    # Parallel async collection of field responses for public overview
    field_responses = await asyncio.gather(*(_get_field_response(field) for field in fields))

    for field, field_res in zip(fields, field_responses):
        response["fields"][field] = field_res

    return Response(response)


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def public_dataset(_request: DrfRequest):
    """
    get:
    Properties of the datasets
    """

    # For now, we don't have any permissions checks for this.
    # In the future, we could introduce a view:dataset permission or something.

    if not settings.CONFIG_PUBLIC:
        return Response(dres.NO_PUBLIC_DATA_AVAILABLE, status=status.HTTP_404_NOT_FOUND)

    # Datasets provenance metadata
    datasets = cm.Dataset.objects.values(
        "title", "description", "contact_info",
        "dates", "stored_in", "spatial_coverage",
        "types", "privacy", "distributions",
        "dimensions", "primary_publications", "citations",
        "produced_by", "creators", "licenses",
        "acknowledges", "keywords", "version", "dats_file",
        "extra_properties", "identifier", "discovery"
    )

    return Response({
        "datasets": datasets
    })


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
    discovery = await discovery_scope.get_discovery()

    # TODO: allow filtering by fields accessed?
    fs_permissions, _ = get_discovery_field_set_permissions(discovery, None, dt_permissions)

    rules = get_rules(discovery, data_permissions=fs_permissions)
    return Response(rules, status=status.HTTP_200_OK)
