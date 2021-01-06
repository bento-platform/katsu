from collections import Counter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets.models import Phenopacket
from .permissions import OverrideOrSuperUserOnly


@api_view(["GET"])
@permission_classes([OverrideOrSuperUserOnly])
def phenopackets_overview(_request):
    phenopackets = Phenopacket.objects.all()

    diseases_counter = Counter()
    phenotypic_features_counter = Counter()

    biosamples_set = set()
    individuals_set = set()

    biosamples_taxonomy = Counter()
    biosamples_sampled_tissue = Counter()

    individuals_sex = Counter()
    individuals_k_sex = Counter()
    individuals_taxonomy = Counter()

    def count_individual(ind):
        individuals_set.add(ind.id)
        individuals_sex.update((ind.sex,))
        individuals_k_sex.update((ind.karyotypic_sex,))
        if ind.taxonomy is not None:
            individuals_taxonomy.update((ind.taxonomy["label"],))

    for p in phenopackets.prefetch_related("biosamples"):
        for b in p.biosamples.all():
            biosamples_set.add(b.id)
            biosamples_sampled_tissue.update((b.sampled_tissue["label"],))

            if b.taxonomy is not None:
                biosamples_taxonomy.update((b.taxonomy["label"],))

            if b.individual is not None:
                count_individual(b.individual)

            for pf in b.phenotypic_features.all():
                phenotypic_features_counter.update((pf.pftype["label"],))

        for d in p.diseases.all():
            diseases_counter.update((d.term["label"],))

        for pf in p.phenotypic_features.all():
            phenotypic_features_counter.update((pf.pftype["label"],))

        # Currently, phenopacket subject is required so we can assume it's not None
        count_individual(p.subject)

    return Response({
        "count": phenopackets.count(),
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
                "sex": {k: individuals_sex[k] for k in (s[0] for s in Individual.SEX)},
                "karyotypic_sex": {k: individuals_k_sex[k] for k in (s[0] for s in Individual.KARYOTYPIC_SEX)},
                "taxonomy": dict(individuals_taxonomy),
                # TODO: how to count age: it can be represented by three different schemas
            },
            "phenotypic_features": {
                # count is a number of unique phenotypic feature types (not all pfs in the database)
                "count": len(phenotypic_features_counter.keys()),
                "type": dict(phenotypic_features_counter)
            },
        }
    })
