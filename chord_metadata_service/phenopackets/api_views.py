from collections import Counter
from rest_framework import viewsets
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from chord_metadata_service.restapi.api_renderers import PhenopacketsRenderer, FHIRRenderer
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination
from chord_metadata_service.restapi.utils import parse_individual_age
from chord_metadata_service.chord.permissions import OverrideOrSuperUserOnly
from chord_metadata_service.phenopackets.schemas import PHENOPACKET_SCHEMA
from . import models as m, serializers as s, filters as f


class PhenopacketsModelViewSet(viewsets.ModelViewSet):
    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, PhenopacketsRenderer)
    pagination_class = LargeResultsSetPagination


class ExtendedPhenopacketsModelViewSet(PhenopacketsModelViewSet):
    renderer_classes = (*PhenopacketsModelViewSet.renderer_classes, FHIRRenderer)


class PhenotypicFeatureViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing phenotypic features

    post:
    Create a new phenotypic feature

    """
    serializer_class = s.PhenotypicFeatureSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.PhenotypicFeatureFilter

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.PhenotypicFeature.objects.filter(
                phenopacket__table__ownership_record__dataset__title__in=allowed_datasets)\
                .order_by("id")
        else:
            queryset = m.PhenotypicFeature.objects.all().order_by("id")
        return queryset


class ProcedureViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing procedures

    post:
    Create a new procedure

    """
    serializer_class = s.ProcedureSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.ProcedureFilter

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.Procedure.objects.filter(
                biosample__phenopacket__table__ownership_record__dataset__title__in=allowed_datasets)\
                .order_by("id")
        else:
            queryset = m.Procedure.objects.all().order_by("id")
        return queryset


class HtsFileViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing HTS files

    post:
    Create a new HTS file

    """
    serializer_class = s.HtsFileSerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.HtsFile.objects\
                .filter(phenopacket__table__ownership_record__dataset__title__in=allowed_datasets)\
                .order_by("uri")
        else:
            queryset = m.HtsFile.objects.all().order_by("uri")
        return queryset


class GeneViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing genes

    post:
    Create a new gene

    """
    serializer_class = s.GeneSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.GeneFilter

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.Gene.objects.filter(phenopacket__table__ownership_record__dataset__title__in=allowed_datasets)\
                .order_by("id")
        else:
            queryset = m.Gene.objects.all().order_by("id")
        return queryset


class VariantViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing variants

    post:
    Create a new variant

    """
    serializer_class = s.VariantSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.VariantFilter

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.Variant.objects\
                .filter(phenopacket__table__ownership_record__dataset__title__in=allowed_datasets)\
                .order_by("id")
        else:
            queryset = m.Variant.objects.all().order_by("id")
        return queryset


class DiseaseViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing diseases

    post:
    Create a new disease

    """
    serializer_class = s.DiseaseSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.DiseaseFilter

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.Disease.objects\
                .filter(phenopacket__table__ownership_record__dataset__title__in=allowed_datasets)\
                .order_by("id")
        else:
            queryset = m.Disease.objects.all().order_by("id")
        return queryset


META_DATA_PREFETCH = (
    "resources",
)


class MetaDataViewSet(PhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing metadata records

    post:
    Create a new metadata record

    """
    serializer_class = s.MetaDataSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.MetaDataFilter

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.MetaData.objects\
                .filter(phenopacket__table__ownership_record__dataset__title__in=allowed_datasets)\
                .prefetch_related(*META_DATA_PREFETCH).order_by("id")
        else:
            queryset = m.MetaData.objects.all().prefetch_related(*META_DATA_PREFETCH).order_by("id")
        return queryset


BIOSAMPLE_PREFETCH = (
    "hts_files",
    "phenotypic_features",
    "procedure",
    "variants",
)


class BiosampleViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing biosamples

    post:
    Create a new biosample
    """
    serializer_class = s.BiosampleSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.BiosampleFilter

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.Biosample.objects.filter(
                phenopacket__table__ownership_record__dataset__title__in=allowed_datasets).\
                prefetch_related(*BIOSAMPLE_PREFETCH).order_by("id")
        else:
            queryset = m.Biosample.objects.all().prefetch_related(*BIOSAMPLE_PREFETCH).order_by("id")
        return queryset


PHENOPACKET_PREFETCH = (
    *(f"biosamples__{p}" for p in BIOSAMPLE_PREFETCH),
    "diseases",
    "genes",
    "hts_files",
    *(f"meta_data__{p}" for p in META_DATA_PREFETCH),
    "phenotypic_features",
    "subject",
    "variants",
)


class PhenopacketViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing phenopackets

    post:
    Create a new phenopacket

    """
    serializer_class = s.PhenopacketSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.PhenopacketFilter

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.Phenopacket.objects.filter(table__ownership_record__dataset__title__in=allowed_datasets).\
                prefetch_related(*PHENOPACKET_PREFETCH).order_by("id")
        else:
            queryset = m.Phenopacket.objects.all().prefetch_related(*PHENOPACKET_PREFETCH).order_by("id")
        return queryset


class GenomicInterpretationViewSet(PhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing genomic interpretations

    post:
    Create a new genomic interpretation

    """
    serializer_class = s.GenomicInterpretationSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.GenomicInterpretationFilter

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.GenomicInterpretation.objects.filter(
                gene__phenopacket__table__ownership_record__dataset__title__in=allowed_datasets)\
                .order_by("id")
        else:
            queryset = m.GenomicInterpretation.objects.all().order_by("id")
        return queryset


class DiagnosisViewSet(PhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing diagnoses

    post:
    Create a new diagnosis

    """
    serializer_class = s.DiagnosisSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.DiagnosisFilter

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.Diagnosis.objects.filter(
                disease__phenopacket__table__ownership_record__dataset__title__in=allowed_datasets)\
                .order_by("id")
        else:
            queryset = m.Diagnosis.objects.all().order_by("id")
        return queryset


class InterpretationViewSet(PhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing interpretations

    post:
    Create a new interpretation

    """
    serializer_class = s.InterpretationSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.InterpretationFilter

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.Interpretation.objects.filter(
                phenopacket__table__ownership_record__dataset__title__in=allowed_datasets)\
                .order_by("id")
        else:
            queryset = m.Interpretation.objects.all().order_by("id")
        return queryset


@api_view(["GET"])
@permission_classes([AllowAny])
def get_chord_phenopacket_schema(_request):
    """
    get:
    Chord phenopacket schema that can be shared with data providers.
    """
    return Response(PHENOPACKET_SCHEMA)


@api_view(["GET"])
@permission_classes([OverrideOrSuperUserOnly])
def phenopackets_overview(_request):
    """
    get:
    Overview of all Phenopackets in the database
    """
    if hasattr(_request, "allowed_datasets_for_counts"):
        allowed_datasets_for_counts = _request.allowed_datasets_for_counts
        phenopackets = m.Phenopacket.objects\
            .filter(table__ownership_record__dataset__title__in=allowed_datasets_for_counts)\
            .prefetch_related(*PHENOPACKET_PREFETCH)
    else:
        phenopackets = m.Phenopacket.objects.all().prefetch_related(*PHENOPACKET_PREFETCH)

    diseases_counter = Counter()
    phenotypic_features_counter = Counter()

    biosamples_set = set()
    individuals_set = set()

    biosamples_taxonomy = Counter()
    biosamples_sampled_tissue = Counter()

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
                # TODO: how to count age: it can be represented by three different schemas
            },
            "phenotypic_features": {
                # count is a number of unique phenotypic feature types (not all pfs in the database)
                "count": len(phenotypic_features_counter.keys()),
                "type": dict(phenotypic_features_counter)
            },
        }
    })
