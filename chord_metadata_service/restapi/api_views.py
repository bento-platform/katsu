from collections import Counter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from chord_metadata_service.phenopackets.api_views import PHENOPACKET_PREFETCH, PHENOPACKET_SELECT_REL
from chord_metadata_service.restapi.utils import parse_individual_age
from chord_metadata_service.chord.permissions import OverrideOrSuperUserOnly
from chord_metadata_service.metadata.service_info import SERVICE_INFO
from chord_metadata_service.phenopackets import models as m


@api_view()
@permission_classes([AllowAny])
def service_info(_request):
    """
    get:
    Return service info
    """

    return Response(SERVICE_INFO)


@api_view(["GET"])
@permission_classes([OverrideOrSuperUserOnly])
def overview(_request):
    """
    get:
    Overview of all Phenopackets in the database
    """
    phenopackets = m.Phenopacket.objects.all().prefetch_related(*PHENOPACKET_PREFETCH).select_related(
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
    individuals_extra_prop = {}
    extra_prop_counter_dict = {}

    def count_individual(ind):

        individuals_set.add(ind.id)
        individuals_sex.update((ind.sex,))
        individuals_k_sex.update((ind.karyotypic_sex,))
        # ethnicity is char field, check it's not empty
        if ind.ethnicity != "":
            individuals_ethnicity.update((ind.ethnicity,))

        # Generic Counter on all available extra properties
        if ind.extra_properties:
            for key in ind.extra_properties:
                # Declare new Counter() if it's not delcared
                if key not in extra_prop_counter_dict:
                    extra_prop_counter_dict[key] = Counter()

                extra_prop_counter_dict[key].update((ind.extra_properties[key],))
                individuals_extra_prop[key] = dict(extra_prop_counter_dict[key])

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
                "sex": {k: individuals_sex[k] for k in (s[0] for s in m.Individual.SEX)},
                "karyotypic_sex": {k: individuals_k_sex[k] for k in (s[0] for s in m.Individual.KARYOTYPIC_SEX)},
                "taxonomy": dict(individuals_taxonomy),
                "age": dict(individuals_age),
                "ethnicity": dict(individuals_ethnicity),
                "extra_properties": dict(individuals_extra_prop),
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
