import asyncio

from adrf.decorators import api_view
from django.conf import settings
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response

from . import responses as dres
from .types import BinWithValue
from ..chord import models as cm
from ..logger import logger

from .fields import get_field_options, get_range_stats, get_categorical_stats, get_date_stats
from .model_lookups import PUBLIC_MODEL_NAMES_TO_MODEL


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
@permission_classes([AllowAny])
async def public_search_fields(_request: DrfRequest):
    """
    get:
    Return public search fields with their configuration
    """

    # TODO: should be project-scoped

    config_public = settings.CONFIG_PUBLIC

    if not config_public:
        return Response(dres.NO_PUBLIC_FIELDS_CONFIGURED, status=status.HTTP_404_NOT_FOUND)

    field_conf = config_public["fields"]

    # Note: the array is wrapped in a dictionary structure to help with JSON
    # processing by some services.

    async def _get_field_response(field) -> dict | None:
        field_props = field_conf[field]

        return {
            **field_props,
            "id": field,
            "options": await get_field_options(field_props, low_counts_censored=True),
        }

    async def _get_section_response(section) -> dict:
        return {
            **section,
            "fields": await asyncio.gather(*filter(None, map(_get_field_response, section["fields"]))),
        }

    return Response({
        "sections": await asyncio.gather(*map(_get_section_response, config_public["search"])),
    })


async def _counts_for_model_name(mn: str) -> tuple[str, int]:
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
@api_view(["GET"])  # Don't use BentoAllowAny, we want to be more careful of cases here.
@permission_classes([AllowAny])
async def public_overview(_request: DrfRequest):
    """
    get:
    Overview of all public data in the database
    """

    config_public = settings.CONFIG_PUBLIC

    if not config_public:
        return Response(dres.NO_PUBLIC_DATA_AVAILABLE, status=status.HTTP_404_NOT_FOUND)

    # TODO: public overviews SHOULD be project-scoped at least.

    # Predefined counts
    counts = dict(await asyncio.gather(*map(_counts_for_model_name, PUBLIC_MODEL_NAMES_TO_MODEL)))

    # Get the rules config - because we used get_config_public_and_field_set_permissions with no arguments, it'll choose
    #  these values based on if we have access to ALL public fields or not.
    rules_config = config_public["rules"]
    count_threshold = rules_config["count_threshold"]

    # Set counts to 0 if they're under the count threshold, and we don't have full data access permissions for the
    # data type corresponding to the model.
    for public_model_name in counts:
        if 0 < counts[public_model_name] <= count_threshold:
            logger.info(f"Public overview: {public_model_name} count is below count threshold")
            counts[public_model_name] = 0

    response = {
        "layout": config_public["overview"],
        "fields": {},
        "counts": {
            "individuals": counts["individual"],
            "biosamples": counts["biosample"],
            "experiments": counts["experiment"],
        },
        # TODO: remove these in favour of public_rules endpoint
        "max_query_parameters": rules_config["max_query_parameters"],
        "count_threshold": count_threshold,
    }

    # Parse the public config to gather data for each field defined in the overview

    fields = [chart["field"] for section in config_public["overview"] for chart in section["charts"]]
    field_conf = config_public["fields"]

    async def _get_field_response(field_id: str, field_props: dict) -> dict:
        stats: list[BinWithValue] | None
        if field_props["datatype"] == "string":
            stats = await get_categorical_stats(field_props, low_counts_censored=True)
        elif field_props["datatype"] == "number":
            stats = await get_range_stats(field_props, low_counts_censored=True)
        elif field_props["datatype"] == "date":
            stats = await get_date_stats(field_props, low_counts_censored=True)
        else:
            raise NotImplementedError()

        return {
            **field_props,
            "id": field_id,
            **({"data": stats} if stats is not None else {}),
        }

    # Parallel async collection of field responses for public overview
    field_responses = await asyncio.gather(*(_get_field_response(field, field_conf[field]) for field in fields))

    for field, field_res in zip(fields, field_responses):
        response["fields"][field] = field_res

    return Response(response)


@api_view(["GET"])
@permission_classes([AllowAny])
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
        "extra_properties", "identifier"
    )

    return Response({
        "datasets": datasets
    })
