import asyncio
import json

from collections import Counter

from adrf.decorators import api_view
from bento_lib.responses import errors
from django.conf import settings
from django.views.decorators.cache import cache_page
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
from chord_metadata_service.authz.permissions import OverrideOrSuperUserOnly, BentoAllowAny
from chord_metadata_service.chord import models as chord_models
from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.experiments import models as experiments_models
from chord_metadata_service.logger import logger
from chord_metadata_service.mcode import models as mcode_models
from chord_metadata_service.mcode.api_views import MCODEPACKET_PREFETCH, MCODEPACKET_SELECT
from chord_metadata_service.metadata.service_info import SERVICE_INFO
from chord_metadata_service.patients import models as patients_models
from chord_metadata_service.phenopackets import models as pheno_models
from chord_metadata_service.restapi.models import SchemaType
from chord_metadata_service.restapi.utils import (
    get_age_numeric_binned,
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
@permission_classes([OverrideOrSuperUserOnly])
async def overview(_request: Request):
    """
    get:
    Overview of all Phenopackets in the database
    """

    # TODO: permissions

    # TODO: parallel
    phenopackets_count = await pheno_models.Phenopacket.objects.all().acount()
    biosamples_count = await pheno_models.Biosample.objects.all().acount()
    individuals_count = await patients_models.Individual.objects.all().acount()
    experiments_count = await experiments_models.Experiment.objects.all().acount()
    experiment_results_count = await experiments_models.ExperimentResult.objects.all().acount()
    instruments_count = await experiments_models.Instrument.objects.all().acount()
    phenotypic_features_count = await pheno_models.PhenotypicFeature.objects.all().distinct('pftype').acount()

    # Sex related fields stats are precomputed here and post processed later
    # to include missing values inferred from the schema
    individuals_sex, individuals_k_sex = await asyncio.gather(
        stats_for_field(patients_models.Individual, "sex"),
        stats_for_field(patients_models.Individual, "karyotypic_sex"),
    )

    diseases_stats = await stats_for_field(pheno_models.Phenopacket, "diseases__term__label")
    diseases_count = len(diseases_stats)

    individuals_age = await get_age_numeric_binned(patients_models.Individual.objects.all(), OVERVIEW_AGE_BIN_SIZE)

    return Response({
        "phenopackets": phenopackets_count,
        "data_type_specific": {
            "biosamples": {
                "count": biosamples_count,
                "taxonomy": await stats_for_field(pheno_models.Biosample, "taxonomy__label"),
                "sampled_tissue": await stats_for_field(pheno_models.Biosample, "sampled_tissue__label"),
            },
            "diseases": {
                # count is a number of unique disease terms (not all diseases in the database)
                "count": diseases_count,
                "term": diseases_stats
            },
            "individuals": {
                "count": individuals_count,
                "sex": {k: individuals_sex.get(k, 0) for k in (s[0] for s in pheno_models.Individual.SEX)},
                "karyotypic_sex": {
                    k: individuals_k_sex.get(k, 0) for k in (s[0] for s in pheno_models.Individual.KARYOTYPIC_SEX)
                },
                "taxonomy": await stats_for_field(patients_models.Individual, "taxonomy__label"),
                "age": individuals_age,
                "ethnicity": await stats_for_field(patients_models.Individual, "ethnicity"),
            },
            "phenotypic_features": {
                # count is a number of unique phenotypic feature types (not all pfs in the database)
                "count": phenotypic_features_count,
                "type": await stats_for_field(pheno_models.PhenotypicFeature, "pftype__label")
            },
            "experiments": {
                "count": experiments_count,
                "study_type": await stats_for_field(experiments_models.Experiment, "study_type"),
                "experiment_type": await stats_for_field(experiments_models.Experiment, "experiment_type"),
                "molecule": await stats_for_field(experiments_models.Experiment, "molecule"),
                "library_strategy": await stats_for_field(experiments_models.Experiment, "library_strategy"),
                "library_source": await stats_for_field(experiments_models.Experiment, "library_source"),
                "library_selection": await stats_for_field(experiments_models.Experiment, "library_selection"),
                "library_layout": await stats_for_field(experiments_models.Experiment, "library_layout"),
                "extraction_protocol": await stats_for_field(experiments_models.Experiment, "extraction_protocol"),
            },
            "experiment_results": {
                "count": experiment_results_count,
                "file_format": await stats_for_field(experiments_models.ExperimentResult, "file_format"),
                "data_output_type": await stats_for_field(experiments_models.ExperimentResult, "data_output_type"),
                "usage": await stats_for_field(experiments_models.ExperimentResult, "usage")
            },
            "instruments": {
                "count": instruments_count,
                "platform": await stats_for_field(experiments_models.Experiment, "instrument__platform"),
                "model": await stats_for_field(experiments_models.Experiment, "instrument__model")
            },
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
@permission_classes([OverrideOrSuperUserOnly])
async def search_overview(request: Request):
    """
    get+post:
    Overview statistics of a list of patients (associated with a search result)
    - Parameter
        - id: a list of patient ids
    """
    individual_id = request.GET.getlist("id") if request.method == "GET" else request.data.get("id", [])
    queryset = patients_models.Individual.objects.all().filter(id__in=individual_id)

    # TODO: filter to only individuals where we have project/dataset-level access? or can we at least pass a dataset
    #  in too to make this less annoying...

    individuals_count = len(individual_id)
    biosamples_count = await (
        queryset
        .values("phenopackets__biosamples__id")
        .exclude(phenopackets__biosamples__id__isnull=True)
        .acount()
    )

    # Sex related fields stats are precomputed here and post processed later
    # to include missing values inferred from the schema
    individuals_sex = await queryset_stats_for_field(queryset, "sex")

    # several obvious approaches to experiment counts give incorrect answers
    experiment_types = await queryset_stats_for_field(
        queryset, "phenopackets__biosamples__experiment__experiment_type")
    experiments_count = sum(experiment_types.values())

    return Response({
        "biosamples": {
            "count": biosamples_count,
            "sampled_tissue": await queryset_stats_for_field(
                queryset, "phenopackets__biosamples__sampled_tissue__label"),
            "histological_diagnosis": await queryset_stats_for_field(
                queryset,
                "phenopackets__biosamples__histological_diagnosis__label"
            ),
        },
        "diseases": {
            "term": await queryset_stats_for_field(queryset, "phenopackets__diseases__term__label"),
        },
        "individuals": {
            "count": individuals_count,
            "sex": {k: individuals_sex.get(k, 0) for k in (s[0] for s in pheno_models.Individual.SEX)},
            "age": await get_age_numeric_binned(queryset, OVERVIEW_AGE_BIN_SIZE),
        },
        "phenotypic_features": {
            "type": await queryset_stats_for_field(queryset, "phenopackets__phenotypic_features__pftype__label"),
        },
        "experiments": {
            "count": experiments_count,
            "experiment_type": experiment_types,
        },
    })


@extend_schema(
    description="Overview of all mCode data in the database",
    responses={
        200: inline_serializer(
            name='mcode_overview_response',
            fields={
                'mcodepackets': serializers.IntegerField(),
                'data_type_specific': serializers.JSONField(),
            }
        ),
    }
)
# Cache page for the requested url for 2 hours
@cache_page(60 * 60 * 2)
@api_view(["GET"])
@permission_classes([OverrideOrSuperUserOnly])
def mcode_overview(_request: Request):
    """
    get:
    Overview of all mCode data in the database
    """
    mcodepackets = mcode_models.MCodePacket.objects.all()\
        .prefetch_related(*MCODEPACKET_PREFETCH)\
        .select_related(*MCODEPACKET_SELECT)

    # cancer condition code
    cancer_condition_counter = Counter()
    # cancer related procedure type - radiation vs. surgical
    cancer_related_procedure_type_counter = Counter()
    # cancer related procedure code
    cancer_related_procedure_counter = Counter()
    # cancer disease status
    cancer_disease_status_counter = Counter()

    individuals_set = set()
    individuals_sex = Counter()
    individuals_k_sex = Counter()
    individuals_taxonomy = Counter()
    individuals_age = Counter()
    individuals_ethnicity = Counter()

    for mcodepacket in mcodepackets:
        # subject/individual
        individual = mcodepacket.subject
        individuals_set.add(individual.id)
        individuals_sex.update((individual.sex,))
        individuals_k_sex.update((individual.karyotypic_sex,))
        if individual.ethnicity != "":
            individuals_ethnicity.update((individual.ethnicity,))
        if individual.taxonomy is not None:
            individuals_taxonomy.update((individual.taxonomy["label"],))
        if mcodepacket.cancer_condition is not None:
            cancer_condition_counter.update((mcodepacket.cancer_condition.condition_type,))
        for cancer_related_procedure in mcodepacket.cancer_related_procedures.all():
            cancer_related_procedure_type_counter.update((cancer_related_procedure.procedure_type,))
            cancer_related_procedure_counter.update((cancer_related_procedure.code["label"],))
        if mcodepacket.cancer_disease_status is not None:
            cancer_disease_status_counter.update((mcodepacket.cancer_disease_status["label"],))

    return Response({
        "mcodepackets": mcodepackets.count(),
        "data_type_specific": {
            "cancer_conditions": {
                "count": len(cancer_condition_counter.keys()),
                "term": dict(cancer_condition_counter)
            },
            "cancer_related_procedure_types": {
                "count": len(cancer_related_procedure_type_counter.keys()),
                "term": dict(cancer_related_procedure_type_counter)
            },
            "cancer_related_procedures": {
                "count": len(cancer_related_procedure_counter.keys()),
                "term": dict(cancer_related_procedure_counter)
            },
            "cancer_disease_status": {
                "count": len(cancer_disease_status_counter.keys()),
                "term": dict(cancer_disease_status_counter)
            },
            "individuals": {
                "count": len(individuals_set),
                "sex": {k: individuals_sex[k] for k in (s[0] for s in pheno_models.Individual.SEX)},
                "karyotypic_sex": {
                    k: individuals_k_sex[k] for k in (s[0] for s in pheno_models.Individual.KARYOTYPIC_SEX)
                },
                "taxonomy": dict(individuals_taxonomy),
                "age": dict(individuals_age),
                "ethnicity": dict(individuals_ethnicity)
            },
        }
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
