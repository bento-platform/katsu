from adrf.decorators import api_view as api_view_async
from drf_spectacular.utils import extend_schema, inline_serializer
from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from chord_metadata_service.restapi.utils import (
    get_age_numeric_binned,
    get_field_options,
    stats_for_field,
    queryset_stats_for_field,
    get_categorical_stats,
    get_date_stats,
    get_range_stats
)
from chord_metadata_service.chord import data_types as dt, models as chord_models
from chord_metadata_service.chord.permissions import OverrideOrSuperUserOnly
from chord_metadata_service.experiments import models as experiments_models
from chord_metadata_service.metadata.service_info import get_service_info
from chord_metadata_service.phenopackets import models as pheno_models
from chord_metadata_service.patients import models as patients_models
from chord_metadata_service.restapi.models import SchemaType
from rest_framework import serializers


OVERVIEW_AGE_BIN_SIZE = 10


@api_view_async()
@permission_classes([AllowAny])
async def service_info(_request):
    """
    get:
    Return service info
    """

    return Response(await get_service_info())


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
def overview(_request):
    """
    get:
    Overview of all Phenopackets in the database
    """
    phenopackets_count = pheno_models.Phenopacket.objects.all().count()
    biosamples_count = pheno_models.Biosample.objects.all().count()
    individuals_count = patients_models.Individual.objects.all().count()
    experiments_count = experiments_models.Experiment.objects.all().count()
    experiment_results_count = experiments_models.ExperimentResult.objects.all().count()
    instruments_count = experiments_models.Instrument.objects.all().count()
    phenotypic_features_count = pheno_models.PhenotypicFeature.objects.all().distinct('pftype').count()

    # Sex related fields stats are precomputed here and post processed later
    # to include missing values inferred from the schema
    individuals_sex = stats_for_field(patients_models.Individual, "sex")
    individuals_k_sex = stats_for_field(patients_models.Individual, "karyotypic_sex")

    diseases_stats = stats_for_field(pheno_models.Phenopacket, "diseases__term__label")
    diseases_count = len(diseases_stats)

    individuals_age = get_age_numeric_binned(patients_models.Individual.objects.all(), OVERVIEW_AGE_BIN_SIZE)

    r = {
        "phenopackets": phenopackets_count,
        "data_type_specific": {
            "biosamples": {
                "count": biosamples_count,
                "taxonomy": stats_for_field(pheno_models.Biosample, "taxonomy__label"),
                "sampled_tissue": stats_for_field(pheno_models.Biosample, "sampled_tissue__label"),
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
                "taxonomy": stats_for_field(patients_models.Individual, "taxonomy__label"),
                "age": individuals_age,
            },
            "phenotypic_features": {
                # count is a number of unique phenotypic feature types (not all pfs in the database)
                "count": phenotypic_features_count,
                "type": stats_for_field(pheno_models.PhenotypicFeature, "pftype__label")
            },
            "experiments": {
                "count": experiments_count,
                "study_type": stats_for_field(experiments_models.Experiment, "study_type"),
                "experiment_type": stats_for_field(experiments_models.Experiment, "experiment_type"),
                "molecule": stats_for_field(experiments_models.Experiment, "molecule"),
                "library_strategy": stats_for_field(experiments_models.Experiment, "library_strategy"),
                "library_source": stats_for_field(experiments_models.Experiment, "library_source"),
                "library_selection": stats_for_field(experiments_models.Experiment, "library_selection"),
                "library_layout": stats_for_field(experiments_models.Experiment, "library_layout"),
                "extraction_protocol": stats_for_field(experiments_models.Experiment, "extraction_protocol"),
            },
            "experiment_results": {
                "count": experiment_results_count,
                "file_format": stats_for_field(experiments_models.ExperimentResult, "file_format"),
                "data_output_type": stats_for_field(experiments_models.ExperimentResult, "data_output_type"),
                "usage": stats_for_field(experiments_models.ExperimentResult, "usage")
            },
            "instruments": {
                "count": instruments_count,
                "platform": stats_for_field(experiments_models.Experiment, "instrument__platform"),
                "model": stats_for_field(experiments_models.Experiment, "instrument__model")
            },
        }
    }

    return Response(r)


@api_view(["GET"])
@permission_classes([OverrideOrSuperUserOnly])
def extra_properties_schema_types(_request):
    """
    get:
    Extra properties schema types
    """
    schema_types = dict(SchemaType.choices)
    return Response(schema_types)


@api_view(["GET", "POST"])
@permission_classes([OverrideOrSuperUserOnly])
def search_overview(request):
    """
    get+post:
    Overview statistics of a list of patients (associated with a search result)
    - Parameter
        - id: a list of patient ids
    """
    individual_id = request.GET.getlist("id") if request.method == "GET" else request.data.get("id", [])
    queryset = patients_models.Individual.objects.all().filter(id__in=individual_id)

    individuals_count = len(individual_id)
    biosamples_count = queryset.values("phenopackets__biosamples__id").exclude(
        phenopackets__biosamples__id__isnull=True).count()

    # Sex related fields stats are precomputed here and post processed later
    # to include missing values inferred from the schema
    individuals_sex = queryset_stats_for_field(queryset, "sex")

    # several obvious approaches to experiment counts give incorrect answers
    experiment_types = queryset_stats_for_field(queryset, "phenopackets__biosamples__experiment__experiment_type")
    experiments_count = sum(experiment_types.values())

    r = {
        "biosamples": {
            "count": biosamples_count,
            "sampled_tissue": queryset_stats_for_field(queryset, "phenopackets__biosamples__sampled_tissue__label"),
            "histological_diagnosis": queryset_stats_for_field(
                queryset,
                "phenopackets__biosamples__histological_diagnosis__label"
            ),
        },
        "diseases": {
            "term": queryset_stats_for_field(queryset, "phenopackets__diseases__term__label"),
        },
        "individuals": {
            "count": individuals_count,
            "sex": {k: individuals_sex.get(k, 0) for k in (s[0] for s in pheno_models.Individual.SEX)},
            "age": get_age_numeric_binned(queryset, OVERVIEW_AGE_BIN_SIZE),
        },
        "phenotypic_features": {
            "type": queryset_stats_for_field(queryset, "phenopackets__phenotypic_features__pftype__label")
        },
        "experiments": {
            "count": experiments_count,
            "experiment_type": experiment_types,
        },
    }
    return Response(r)


@extend_schema(
    description="Public search fields with their configuration",
    responses={
        200: inline_serializer(
            name='public_search_fields_response',
            fields={
                'sections': serializers.JSONField(),
            }
        )
    }
)
@api_view(["GET"])
@permission_classes([AllowAny])
def public_search_fields(_request):
    """
    get:
    Return public search fields with their configuration
    """
    if not settings.CONFIG_PUBLIC:
        return Response(settings.NO_PUBLIC_FIELDS_CONFIGURED)

    search_conf = settings.CONFIG_PUBLIC["search"]
    field_conf = settings.CONFIG_PUBLIC["fields"]
    # Note: the array is wrapped in a dictionary structure to help with JSON
    # processing by some services.
    r = {
        "sections": [
            {
                **section,
                "fields": [
                    {
                        **field_conf[f],
                        "id": f,
                        "options": get_field_options(field_conf[f])
                    } for f in section["fields"]
                ]
            } for section in search_conf
        ]
    }
    return Response(r)


@extend_schema(
    description="Overview of all public data in the database",
    responses={
        200: inline_serializer(
            name='public_overview_response',
            fields={
                'datasets': serializers.CharField(),
            }
        )
    }
)
@api_view(["GET"])
@permission_classes([AllowAny])
def public_overview(_request):
    """
    get:
    Overview of all public data in the database
    """

    if not settings.CONFIG_PUBLIC:
        return Response(settings.NO_PUBLIC_DATA_AVAILABLE)

    # Predefined counts
    individuals_count = patients_models.Individual.objects.all().count()
    biosamples_count = pheno_models.Biosample.objects.all().count()
    experiments_count = experiments_models.Experiment.objects.all().count()

    # Early return when there is not enough data
    if individuals_count < settings.CONFIG_PUBLIC["rules"]["count_threshold"]:
        return Response(settings.INSUFFICIENT_DATA_AVAILABLE)

    # Get the rules config
    rules_config = settings.CONFIG_PUBLIC["rules"]

    response = {
        "layout": settings.CONFIG_PUBLIC["overview"],
        "fields": {},
        "counts": {
            "individuals": individuals_count,
            "biosamples": biosamples_count,
            "experiments": experiments_count
        },
        "max_query_parameters": rules_config["max_query_parameters"],
        "count_threshold": rules_config["count_threshold"],
    }

    # Parse the public config to gather data for each field defined in the
    # overview
    fields = [chart["field"] for section in settings.CONFIG_PUBLIC["overview"] for chart in section["charts"]]

    for field in fields:
        field_props = settings.CONFIG_PUBLIC["fields"][field]
        if field_props["datatype"] == "string":
            stats = get_categorical_stats(field_props)
        elif field_props["datatype"] == "number":
            stats = get_range_stats(field_props)
        elif field_props["datatype"] == "date":
            stats = get_date_stats(field_props)
        else:
            raise NotImplementedError()

        response["fields"][field] = {
            **field_props,
            "id": field,
            "data": stats
        }

    return Response(response)


@api_view(["GET"])
@permission_classes([AllowAny])
def public_dataset(_request):
    """
    get:
    Properties of the datasets
    """

    if not settings.CONFIG_PUBLIC:
        return Response(settings.NO_PUBLIC_DATA_AVAILABLE)

    # Datasets provenance metadata
    datasets = chord_models.Dataset.objects.values(
        "title", "description", "contact_info",
        "dates", "stored_in", "spatial_coverage",
        "types", "privacy", "distributions",
        "dimensions", "primary_publications", "citations",
        "produced_by", "creators", "licenses",
        "acknowledges", "keywords", "version", "dats_file",
        "extra_properties", "identifier"
    )

    # convert dats_file json content to dict
    # datasets = [
    #     {
    #         **d,
    #         "dats_file": json.loads(d["dats_file"]) if d["dats_file"] else None
    #     } for d in datasets]

    return Response({
        "datasets": datasets
    })


DT_QUERYSETS = {
    dt.DATA_TYPE_EXPERIMENT: experiments_models.Experiment.objects.all(),
    dt.DATA_TYPE_PHENOPACKET: pheno_models.Phenopacket.objects.all(),
}
