import math
import logging

from collections import Counter
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.db.models import Count
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from chord_metadata_service.restapi.utils import parse_individual_age
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
    diseases_count = pheno_models.Disease.objects.all().count()
    biosamples_count = pheno_models.Biosample.objects.all().count()
    individuals_count = patients_models.Individual.objects.all().count()
    experiments_count = experiments_models.Experiment.objects.all().count()
    experiment_results_count = experiments_models.ExperimentResult.objects.all().count()
    instruments_count = experiments_models.Instrument.objects.all().count()
    phenotypic_features_count = pheno_models.PhenotypicFeature.objects.all().distinct('pftype').count()

    individuals_sex = stats_for_field(patients_models.Individual, "sex")
    individuals_k_sex = stats_for_field(patients_models.Individual, "karyotypic_sex")

    r = {
        "phenopackets": phenopackets_count,
        "data_type_specific": {
            "biosamples": {
                "count": biosamples_count,
                "taxonomy": stats_for_field(pheno_models.Biosample, "taxonomy", "label"),
                "sampled_tissue": stats_for_field(pheno_models.Biosample, "sampled_tissue", "label"),
            },
            "diseases": {
                # count is a number of unique disease terms (not all diseases in the database)
                "count": diseases_count,
                "term": stats_for_field(pheno_models.Disease, "term", "label")
            },
            "individuals": {
                "count": individuals_count,
                "sex": {k: individuals_sex.get(k, 0) for k in (s[0] for s in pheno_models.Individual.SEX)},
                "karyotypic_sex": {
                    k: individuals_k_sex.get(k, 0) for k in (s[0] for s in pheno_models.Individual.KARYOTYPIC_SEX)
                },
                "taxonomy": stats_for_field(patients_models.Individual, "taxonomy", "label"),
                "age": dict(),  # dict(individuals_age),
                "ethnicity": stats_for_field(patients_models.Individual, "ethnicity"),
                # "extra_properties": dict(individuals_extra_prop),
            },
            "phenotypic_features": {
                # count is a number of unique phenotypic feature types (not all pfs in the database)
                "count": phenotypic_features_count,
                "type": stats_for_field(pheno_models.PhenotypicFeature, "pftype", "label")
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
                "platform": stats_for_field(experiments_models.Instrument, "platform"),
                "model": stats_for_field(experiments_models.Instrument, "model")
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
    Return public search fields
    """
    if settings.CONFIG_FIELDS:
        return Response(settings.CONFIG_FIELDS)
    else:
        return Response(settings.NO_PUBLIC_FIELDS_CONFIGURED)


@api_view(["GET"])
@permission_classes([AllowAny])
def public_overview(_request):
    """
    get:
    Overview of all public data in the database
    """

    # TODO should this be added to the project config.json file ?
    threshold = 5
    missing = "missing"

    if settings.CONFIG_FIELDS:

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

        individuals = patients_models.Individual.objects.all()
        individuals_set = set()
        individuals_sex = Counter()
        individuals_age = Counter()
        individuals_extra_properties = {}
        extra_properties = {}

        experiments = experiments_models.Experiment.objects.all()
        experiments_set = set()
        experiments_type = Counter()

        for individual in individuals:
            # subject/individual
            individuals_set.add(individual.id)
            individuals_sex.update((individual.sex,))
            # age
            if individual.age is not None:
                individuals_age.update((parse_individual_age(individual.age),))
            # collect extra_properties defined in config
            if individual.extra_properties and "extra_properties" in settings.CONFIG_FIELDS:
                for key in individual.extra_properties:
                    if key in settings.CONFIG_FIELDS["extra_properties"]:
                        # add new Counter()
                        if key not in extra_properties:
                            extra_properties[key] = Counter()
                        try:
                            extra_properties[key].update((individual.extra_properties[key],))
                        except TypeError:
                            logger.error(f"The extra_properties {key} value is not of type string or number.")
                            pass

                        individuals_extra_properties[key] = dict(extra_properties[key])
        # Experiments
        for experiment in experiments:
            experiments_set.add(experiment.id)
            experiments_type.update((experiment.experiment_type,))

        # Put age in bins
        if individuals_age:
            age_bin_size = settings.CONFIG_FIELDS["age"]["bin_size"] \
                if "age" in settings.CONFIG_FIELDS and "bin_size" in settings.CONFIG_FIELDS["age"] else None
            age_kwargs = dict(values=dict(individuals_age), bin_size=age_bin_size)
            individuals_age_bins = sort_numeric_values_into_bins(
                **{k: v for k, v in age_kwargs.items() if v is not None}
            )
        else:
            individuals_age_bins = {}

        # Put all other numeric values coming from extra_properties in bins and remove values where count <= threshold
        if individuals_extra_properties:
            for key, value in list(individuals_extra_properties.items()):
                # extra_properties contains only the fields specified in config
                if settings.CONFIG_FIELDS["extra_properties"][key]["type"] == "number":
                    # retrieve bin_size if available
                    field_bin_size = settings.CONFIG_FIELDS["extra_properties"][key]["bin_size"] \
                        if "bin_size" in settings.CONFIG_FIELDS["extra_properties"][key] else None
                    # retrieve the values from extra_properties counter
                    values = individuals_extra_properties[key]
                    if values:
                        kwargs = dict(values=values, bin_size=field_bin_size)
                        # sort into bins and remove numeric values where count <= threshold
                        extra_prop_values_in_bins = sort_numeric_values_into_bins(
                            **{k: v for k, v in kwargs.items() if v is not None}
                        )
                        # rewrite with sorted values
                        individuals_extra_properties[key] = extra_prop_values_in_bins
                    # add missing value count
                    individuals_extra_properties[key][missing] = len(individuals_set) - sum(v for v in value.values())
                else:
                    # add missing value count
                    value[missing] = len(individuals_set) - sum(v for v in value.values())
                    # remove string values where count <= threshold
                    for k, v in list(value.items()):
                        if v <= 5 and k != missing:
                            individuals_extra_properties[key].pop(k)

        # Update counters with missing values
        for counter, all_values in zip([individuals_sex, individuals_age_bins], [individuals_sex, individuals_age]):
            counter[missing] = len(individuals_set) - sum(v for v in dict(all_values).values())

        # Response content
        if len(individuals_set) < threshold:
            content = settings.INSUFFICIENT_DATA_AVAILABLE
        else:
            content = {
                "individuals": len(individuals_set)
            }
            for field, value in zip(
                    ["sex", "age", "extra_properties", "experiment_type"],
                    [{k: v for k, v in dict(individuals_sex).items() if v > threshold or k == missing},
                     individuals_age_bins,
                     individuals_extra_properties,
                     dict(experiments_type)]):
                if field in settings.CONFIG_FIELDS:
                    content[field] = value
            if "experiment_type" in content:
                content["experiments"] = len(experiments_set)
            content["datasets"] = datasets
        return Response(content)

    else:
        return Response(settings.NO_PUBLIC_DATA_AVAILABLE)


def sort_numeric_values_into_bins(values: dict, bin_size: int = 10, threshold: int = 5):
    values_in_bins = {}
    # convert keys to int
    keys_to_int_values = {int(k): v for k, v in values.items()}
    # find the max value and define the  range
    for j in range(math.ceil(max(keys_to_int_values.keys()) / bin_size)):
        bin_key = j * bin_size
        keys = [a for a in keys_to_int_values.keys() if j * bin_size <= a < (j + 1) * bin_size]
        keys_sum = 0
        for k, v in keys_to_int_values.items():
            if k in keys:
                keys_sum += v
        values_in_bins[f"{bin_key}"] = keys_sum
    # remove data if count < 5
    return {k: v for k, v in values_in_bins.items() if v > threshold}


def stats_for_field(model, field: str, label_field: str = None):
    # values() restrict the table of results to this field
    # annotate() creates a `total` column for the aggregation
    # Count() aggregates the results by performing a group by on the field
    query_set = model.objects.all().values(field).annotate(total=Count(field))
    stats = dict()
    for item in list(query_set):
        key = item[field]
        if key is None:
            continue

        if label_field:
            key = item[field][label_field]
        stats[key] = item['total']
    return stats
