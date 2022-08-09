import logging

from collections import Counter

from django.conf import settings
from django.views.decorators.cache import cache_page
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from chord_metadata_service.restapi.utils import (
    get_field_options,
    parse_individual_age,
    stats_for_field,
    compute_binned_ages,
    get_field_bins,
    get_categorical_stats,
    get_date_stats,
    get_range_stats
)
from chord_metadata_service.chord.permissions import OverrideOrSuperUserOnly
from chord_metadata_service.metadata.service_info import SERVICE_INFO
from chord_metadata_service.chord import models as chord_models
from chord_metadata_service.phenopackets import models as pheno_models
from chord_metadata_service.mcode import models as mcode_models
from chord_metadata_service.patients import models as patients_models
from chord_metadata_service.experiments import models as experiments_models
from chord_metadata_service.mcode.api_views import MCODEPACKET_PREFETCH, MCODEPACKET_SELECT


logger = logging.getLogger("restapi_api_views")
logger.setLevel(logging.INFO)

OVERVIEW_AGE_BIN_SIZE = 10


@api_view()
@permission_classes([AllowAny])
def service_info(_request):
    """
    get:
    Return service info
    """

    return Response(SERVICE_INFO)


# Cache page for the requested url for 2 hours
@cache_page(60 * 60 * 2)
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

    # age_numeric is computed at ingestion time of phenopackets. On some instances
    # it might be unavailable and as a fallback must be computed from the age JSON field which
    # has two alternate formats (hence more complex and slower to process)
    individuals_age = get_field_bins(patients_models.Individual, "age_numeric", OVERVIEW_AGE_BIN_SIZE)
    if None in individuals_age:  # fallback
        del individuals_age[None]
        individuals_age = Counter(individuals_age)
        individuals_age.update(
            compute_binned_ages(OVERVIEW_AGE_BIN_SIZE)   # single update instead of creating iterables in a loop
        )

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
                "ethnicity": stats_for_field(patients_models.Individual, "ethnicity"),
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


# Cache page for the requested url for 2 hours
@cache_page(60 * 60 * 2)
@api_view(["GET"])
@permission_classes([OverrideOrSuperUserOnly])
def mcode_overview(_request):
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
        if individual.age is not None:
            individuals_age.update((parse_individual_age(individual.age),))
        if individual.taxonomy is not None:
            individuals_taxonomy.update((individual.taxonomy["label"],))
        for cancer_condition in mcodepacket.cancer_condition.all():
            cancer_condition_counter.update((cancer_condition.code["label"],))
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
    experiments_count = experiments_models.Experiment.objects.all().count()

    # Early return when there is not enough data
    if individuals_count < settings.CONFIG_PUBLIC["rules"]["count_threshold"]:
        return Response(settings.INSUFFICIENT_DATA_AVAILABLE)

    # Datasets provenance metadata
    datasets = chord_models.Dataset.objects.values(
        "title", "description", "contact_info",
        "dates", "stored_in", "spatial_coverage",
        "types", "privacy", "distributions",
        "dimensions", "primary_publications", "citations",
        "produced_by", "creators", "licenses",
        "acknowledges", "keywords", "version",
        "extra_properties"
    )

    response = {
        "datasets": datasets,
        "layout": settings.CONFIG_PUBLIC["overview"],
        "fields": {},
        "counts": {
            "individuals": individuals_count,
            "experiments": experiments_count
        },
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

        response["fields"][field] = {
            **field_props,
            "id": field,
            "data": stats
        }

    return Response(response)
