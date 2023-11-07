import asyncio
import json

from adrf.decorators import api_view
from bento_lib.auth.permissions import P_QUERY_DATA
from bento_lib.auth.resources import build_resource
from bento_lib.responses import errors
from django.conf import settings
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from chord_metadata_service.authz.discovery import (
    DiscoveryPermissionsDict,
    DataTypeDiscoveryPermissions,
    get_data_type_discovery_permissions,
)
from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.authz.permissions import BentoAllowAny
from chord_metadata_service.chord import models as chord_models
from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.experiments import models as experiments_models, summaries as exp_summaries
from chord_metadata_service.logger import logger
from chord_metadata_service.metadata.service_info import SERVICE_INFO
from chord_metadata_service.patients import models as patients_models, summaries as patient_summaries
from chord_metadata_service.phenopackets import models as pheno_models, summaries as pheno_summaries
from chord_metadata_service.restapi.models import SchemaType
from chord_metadata_service.restapi.utils import (
    get_public_model_name_and_field_path,
    get_field_options,
    stats_for_field,
    queryset_stats_for_field,
    get_categorical_stats,
    get_date_stats,
    get_range_stats,
    PUBLIC_MODEL_NAMES_TO_MODEL,
    PUBLIC_MODEL_NAMES_TO_DATA_TYPE,
    BinWithValue,
)

OVERVIEW_AGE_BIN_SIZE = 10


@api_view(["GET"])
@permission_classes([BentoAllowAny])
def service_info(_request: Request):
    """
    get:
    Return service info
    """

    return Response(SERVICE_INFO)


@extend_schema(
    description="Overview of all Phenopackets in the database",
    responses={
        200: inline_serializer(
            name='overview_response',
            fields={
                'phenopackets': serializers.IntegerField(),
                'data_type_specific': serializers.JSONField(),
            }
        )
    }
)
@api_view(["GET"])
async def overview(_request: Request):
    """
    get:
    Overview of all Phenopackets in the database
    """

    # TODO: permissions

    phenopackets = pheno_models.Phenopacket.objects.all()
    experiments = experiments_models.Experiment.objects.all()

    # Parallel-gather all statistics we may need for this response
    (
        phenopackets_count,
        biosample_summary,
        individual_summary,
        disease_summary,
        pf_summary,
        experiment_summary,
        exp_res_summary,
        instrument_summary,
    ) = await asyncio.gather(
        phenopackets.acount(),
        pheno_summaries.biosample_summary(phenopackets),
        patient_summaries.individual_summary(phenopackets),
        pheno_summaries.disease_summary(phenopackets),
        pheno_summaries.phenotypic_feature_summary(phenopackets),
        exp_summaries.experiment_summary(experiments),
        exp_summaries.experiment_result_summary(experiments),
        exp_summaries.instrument_summary(experiments),
    )

    return Response({
        "phenopackets": phenopackets_count,
        "data_type_specific": {
            "biosamples": biosample_summary,
            "diseases": disease_summary,
            "individuals": individual_summary,
            "phenotypic_features": pf_summary,
            "experiments": experiment_summary,
            "experiment_results": exp_res_summary,
            "instruments": instrument_summary,
        }
    })


@api_view(["GET"])
@permission_classes([BentoAllowAny])
def extra_properties_schema_types(_request: Request):
    """
    get:
    Extra properties schema types
    """
    schema_types = dict(SchemaType.choices)
    return Response(schema_types)


@api_view(["GET", "POST"])
async def search_overview(request: Request):
    """
    get+post:
    Overview statistics of a list of patients (associated with a search result)
    - Parameter
        - id: a list of patient ids
    """

    individual_ids = request.GET.getlist("id") if request.method == "GET" else request.data.get("id", [])

    queryset = patients_models.Individual.objects.all().filter(id__in=individual_ids)

    datasets_accessed = frozenset({ds_id async for ds_id in (
        queryset
        .exclude(phenopackets__dataset_id__isnull=True)
        .values_list("phenopackets__dataset__project__identifier", "phenopackets__dataset__identifier")
    )})

    # IMPORTANT PERMISSIONS NOTE: ----–----–----–----–----–----–----–----–----–----–------------------------------------
    # Even though we're basically just accessing counts here, we require the query:data permissions since otherwise
    # users could discover the ID format/which IDs exist in the instance (BAD!!!)
    # ------------------------------------------------------------------------------------------------------------------

    authz_resources = tuple(build_resource(project=d[0], dataset=d[1]) for d in datasets_accessed)
    auth_res = await authz_middleware.async_evaluate(request, authz_resources, (P_QUERY_DATA,))
    allowed_datasets = tuple(r["dataset"] for r, p in zip(authz_resources, auth_res) if p[0])

    authorized_individuals = queryset.filter(phenopackets__dataset_id__in=allowed_datasets)
    # We need to select these separately, since we could be authorized to access one phenopacket for an individual
    # but not another - thus we get just phenopackets we're authorized to get for individuals we selected:
    authorized_phenopackets = pheno_models.Phenopacket.objects.filter(
        subject__in=authorized_individuals, dataset_id__in=allowed_datasets)

    # TODO: this hardcodes the biosample linked field set relationship
    #  - in general, this endpoint is less than ideal and should be derived from search results themselves vs. this
    #    hack-y mess of passing IDs around.
    authorized_experiments = experiments_models.Experiment.objects.filter(
        dataset_id__in=allowed_datasets,
        biosample_id__in=authorized_phenopackets.values_list("biosample_id", flat=True),
    )

    return Response({
        "biosamples": await pheno_summaries.biosample_summary(authorized_phenopackets),
        "diseases": await pheno_summaries.disease_summary(authorized_phenopackets),
        "individuals": await patient_summaries.individual_summary(authorized_phenopackets),
        "phenotypic_features": await pheno_summaries.phenotypic_feature_summary(authorized_phenopackets),
        "experiments": await exp_summaries.experiment_summary(authorized_experiments),
    })


async def get_public_data_type_permissions(request: Request) -> DataTypeDiscoveryPermissions:
    return await get_data_type_discovery_permissions(
        request,

        # Collect all data types that we need permissions for to give various parts of the public overview response.
        #  - individuals & biosamples are in the 'phenopacket' data type, experiments are in the 'experiment' data type
        list(set(PUBLIC_MODEL_NAMES_TO_DATA_TYPE.values()))
    )


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
async def public_search_fields(request: Request):
    """
    get:
    Return public search fields with their configuration
    """

    # TODO: should be project-scoped

    config_public = settings.CONFIG_PUBLIC

    if not config_public:
        authz_middleware.mark_authz_done(request)
        return Response(settings.NO_PUBLIC_FIELDS_CONFIGURED, status=status.HTTP_404_NOT_FOUND)

    # Access (counts/data) permissions by Bento data type
    dt_permissions = await get_public_data_type_permissions(request)

    field_conf = config_public["fields"]

    # Note: the array is wrapped in a dictionary structure to help with JSON
    # processing by some services.

    async def _get_field_response(field) -> dict:
        field_props = field_conf[field]
        field_perms = get_count_and_query_data_permissions_for_field(dt_permissions, field_props)

        return {
            **field_props,
            "id": field,
            "options": await get_field_options(field_props, low_counts_censored=not field_perms["data"]),
        }

    async def _get_section_response(section) -> dict:
        return {
            **section,
            "fields": await asyncio.gather(*map(_get_field_response, section["fields"])),
        }

    return Response({
        "sections": await asyncio.gather(*map(_get_section_response, config_public["search"])),
    })


def get_count_and_query_data_permissions_for_field(
    dt_permissions: DataTypeDiscoveryPermissions, field_props: dict
) -> DiscoveryPermissionsDict:
    public_model_name, _ = get_public_model_name_and_field_path(field_props["mapping"])
    field_bento_data_type = PUBLIC_MODEL_NAMES_TO_DATA_TYPE[public_model_name]
    return dt_permissions[field_bento_data_type]


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
async def public_overview(request: Request):
    """
    get:
    Overview of all public data in the database
    """

    config_public = settings.CONFIG_PUBLIC

    if not config_public:
        authz_middleware.mark_authz_done(request)
        return Response(settings.NO_PUBLIC_DATA_AVAILABLE, status=status.HTTP_404_NOT_FOUND)

    # TODO: public overviews SHOULD be project-scoped at least.

    # Access (counts/data) permissions by Bento data type
    dt_permissions = await get_public_data_type_permissions(request)

    # If we don't have AT LEAST one count permission, assume we're not supposed to see this page and return forbidden.
    if not any(dpd["counts"] for dpd in dt_permissions.values()):
        authz_middleware.mark_authz_done(request)
        return Response(errors.forbidden_error(), status=status.HTTP_403_FORBIDDEN)

    # Predefined counts
    async def _counts_for_model_name(mn: str) -> tuple[str, int]:
        return mn, await PUBLIC_MODEL_NAMES_TO_MODEL[mn].objects.all().acount()
    counts = dict(await asyncio.gather(*map(_counts_for_model_name, PUBLIC_MODEL_NAMES_TO_MODEL)))

    # Get the rules config
    rules_config = settings.CONFIG_PUBLIC["rules"]
    count_threshold = rules_config["count_threshold"]

    # Set counts to 0 if they're under the count threshold, and we don't have full data access permissions for the
    # data type corresponding to the model.
    for public_model_name in counts:
        data_type = PUBLIC_MODEL_NAMES_TO_DATA_TYPE[public_model_name]
        if 0 < counts[public_model_name] <= count_threshold and not dt_permissions[data_type]["data"]:
            logger.info(f"Public overview: {public_model_name} count is below count threshold")
            counts[public_model_name] = 0

    response = {
        "layout": config_public["overview"],
        "fields": {},
        "counts": {
            **({
                "individuals": counts["individual"],
                "biosamples": counts["biosample"],
            } if dt_permissions[DATA_TYPE_PHENOPACKET]["counts"] else {}),
            **({
                "experiments": counts["experiment"],
            } if dt_permissions[DATA_TYPE_EXPERIMENT]["counts"] else {}),
        },
        "max_query_parameters": rules_config["max_query_parameters"],
        "count_threshold": count_threshold,
    }

    # Parse the public config to gather data for each field defined in the overview

    fields = [chart["field"] for section in config_public["overview"] for chart in section["charts"]]
    field_conf = config_public["fields"]

    async def _get_field_response(field_id: str, field_props: dict) -> dict:
        field_perms = get_count_and_query_data_permissions_for_field(dt_permissions, field_props)

        # Permissions incorporation: only censor small cell counts when we don't have query:data access
        stats: list[BinWithValue] | None
        if not field_perms["counts"]:
            stats = None
        elif field_props["datatype"] == "string":
            stats = await get_categorical_stats(field_props, low_counts_censored=not field_perms["data"])
        elif field_props["datatype"] == "number":
            stats = await get_range_stats(field_props, low_counts_censored=not field_perms["data"])
        elif field_props["datatype"] == "date":
            stats = await get_date_stats(field_props, low_counts_censored=not field_perms["data"])
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

    authz_middleware.mark_authz_done(request)
    return Response(response)


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def public_dataset(_request: Request):
    """
    get:
    Properties of the datasets
    """

    # For now, we don't have any permissions checks for this.
    # In the future, we could introduce a view:dataset permission or something.

    if not settings.CONFIG_PUBLIC:
        return Response(settings.NO_PUBLIC_DATA_AVAILABLE, status=status.HTTP_404_NOT_FOUND)

    return Response({
        "datasets": [
            {
                **d,
                # convert dats_file json content to dict
                "dats_file": json.loads(d["dats_file"]) if d["dats_file"] else None,
            }
            async for d in (
                # Datasets provenance metadata:
                chord_models.Dataset.objects.values(
                    "title", "description", "contact_info",
                    "dates", "stored_in", "spatial_coverage",
                    "types", "privacy", "distributions",
                    "dimensions", "primary_publications", "citations",
                    "produced_by", "creators", "licenses",
                    "acknowledges", "keywords", "version", "dats_file",
                    "extra_properties", "identifier"
                )
            )
        ]
    })
