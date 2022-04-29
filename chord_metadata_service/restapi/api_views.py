import math
import logging

from collections import Counter
from django.conf import settings
from django.views.decorators.cache import cache_page
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from chord_metadata_service.phenopackets.api_views import PHENOPACKET_PREFETCH, PHENOPACKET_SELECT_REL
from chord_metadata_service.restapi.utils import parse_individual_age
from chord_metadata_service.chord.permissions import OverrideOrSuperUserOnly
from chord_metadata_service.metadata.service_info import SERVICE_INFO
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
    phenopackets = pheno_models.Phenopacket.objects.all().prefetch_related(*PHENOPACKET_PREFETCH).select_related(
        *PHENOPACKET_SELECT_REL)

    diseases_counter = Counter()
    phenotypic_features_counter = Counter()

    biosamples_set = set()
    individuals_set = set()

    biosamples_taxonomy = Counter()
    biosamples_sampled_tissue = Counter()

    experiments_set = set()
    experiments = {
        "study_type": Counter(),
        "experiment_type": Counter(),
        "molecule": Counter(),
        "library_strategy": Counter(),
        "library_source": Counter(),
        "library_selection": Counter(),
        "library_layout": Counter(),
        "extraction_protocol": Counter()
    }
    experiment_results_set = set()
    experiment_results = {
        "file_format": Counter(),
        "data_output_type": Counter(),
        "usage": Counter(),
    }
    instrument_set = set()
    instruments = {
        "platform": Counter(),
        "model": Counter(),
    }

    individuals_sex = Counter()
    individuals_k_sex = Counter()
    individuals_taxonomy = Counter()
    individuals_age = Counter()
    individuals_ethnicity = Counter()
    # individuals_extra_prop = {}
    # extra_prop_counter_dict = {}

    def count_individual(ind):

        individuals_set.add(ind.id)
        individuals_sex.update((ind.sex,))
        individuals_k_sex.update((ind.karyotypic_sex,))
        # ethnicity is char field, check it's not empty
        if ind.ethnicity != "":
            individuals_ethnicity.update((ind.ethnicity,))

        # Generic Counter on all available extra properties
        # Comment out this count for now since it explodes the response
        # if ind.extra_properties:
        #     for key in ind.extra_properties:
        #         # Declare new Counter() if it's not delcared
        #         if key not in extra_prop_counter_dict:
        #             extra_prop_counter_dict[key] = Counter()
        #
        #         extra_prop_counter_dict[key].update((ind.extra_properties[key],))
        #         individuals_extra_prop[key] = dict(extra_prop_counter_dict[key])

        if ind.age is not None:
            individuals_age.update((parse_individual_age(ind.age),))
        if ind.taxonomy is not None:
            individuals_taxonomy.update((ind.taxonomy["label"],))

    for p in phenopackets:
        for b in p.biosamples.all():
            biosamples_set.add(b.id)
            biosamples_sampled_tissue.update((b.sampled_tissue["label"],))

            if b.taxonomy is not None:
                biosamples_taxonomy.update((b.taxonomy["label"],))

            for exp in b.experiment_set.all():
                experiments_set.add(exp.id)

                # local function to perform count across all fields in a given object
                def count_object_fields(obj, container: dict):
                    for field, value in container.items():
                        if getattr(obj, field) is not None:
                            container[field].update((getattr(obj, field),))

                count_object_fields(exp, experiments)

                # query_set.many_to_many.all()
                if exp.experiment_results.all() is not None:
                    for result in exp.experiment_results.all():
                        experiment_results_set.add(result.id)
                        count_object_fields(result, experiment_results)

                if exp.instrument is not None:
                    instrument_set.add(exp.instrument.id)
                    count_object_fields(exp.instrument, instruments)

            # TODO decide what to do with nested Phenotypic features and Subject in Biosample
            # This might serve future use cases that Biosample as a have main focus of study
            # for pf in b.phenotypic_features.all():
            #     phenotypic_features_counter.update((pf.pftype["label"],))

        # according to Phenopackets standard
        # phenotypic features also can be linked to a Biosample
        # but we count them here because all our use cases current have them linked to Phenopacket not biosample
        for d in p.diseases.all():
            diseases_counter.update((d.term["label"],))

        for pf in p.phenotypic_features.all():
            phenotypic_features_counter.update((pf.pftype["label"],))

        # Currently, phenopacket subject is required so we can assume it's not None
        count_individual(p.subject)

    return Response({
        "phenopackets": phenopackets.count(),
        "data_type_specific": {
            "biosamples": {
                "count": len(biosamples_set),
                "taxonomy": dict(biosamples_taxonomy),
                "sampled_tissue": dict(biosamples_sampled_tissue),
            },
            "diseases": {
                # count is a number of unique disease terms (not all diseases in the database)
                "count": len(diseases_counter.keys()),
                "term": dict(diseases_counter)
            },
            "individuals": {
                "count": len(individuals_set),
                "sex": {k: individuals_sex[k] for k in (s[0] for s in pheno_models.Individual.SEX)},
                "karyotypic_sex": {
                    k: individuals_k_sex[k] for k in (s[0] for s in pheno_models.Individual.KARYOTYPIC_SEX)
                },
                "taxonomy": dict(individuals_taxonomy),
                "age": dict(individuals_age),
                "ethnicity": dict(individuals_ethnicity),
                # "extra_properties": dict(individuals_extra_prop),
            },
            "phenotypic_features": {
                # count is a number of unique phenotypic feature types (not all pfs in the database)
                "count": len(phenotypic_features_counter.keys()),
                "type": dict(phenotypic_features_counter)
            },
            "experiments": {
                "count": len(experiments_set),
                "study_type": dict(experiments["study_type"]),
                "experiment_type": dict(experiments["experiment_type"]),
                "molecule": dict(experiments["molecule"]),
                "library_strategy": dict(experiments["library_strategy"]),
                "library_source": dict(experiments["library_source"]),
                "library_selection": dict(experiments["library_selection"]),
                "library_layout": dict(experiments["library_layout"]),
                "extraction_protocol": dict(experiments["extraction_protocol"]),
            },
            "experiment_results": {
                "count": len(experiment_results_set),
                "file_format": dict(experiment_results["file_format"]),
                "data_output_type": dict(experiment_results["data_output_type"]),
                "usage": dict(experiment_results["usage"])
            },
            "instruments": {
                "count": len(instrument_set),
                "platform": dict(instruments["platform"]),
                "model": dict(instruments["model"])
            },
        }
    })


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
