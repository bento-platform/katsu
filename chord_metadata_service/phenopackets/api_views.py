from rest_framework import viewsets
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from chord_metadata_service.restapi.api_renderers import PhenopacketsRenderer, FHIRRenderer
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination
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
                .filter(biosample__phenopacket__table__ownership_record__dataset__title__in=allowed_datasets)\
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
    "experiment_set",
)

BIOSAMPLE_SELECT_REL = (
    "procedure",
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
                prefetch_related(*BIOSAMPLE_PREFETCH).select_related(*BIOSAMPLE_SELECT_REL).order_by("id")
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

PHENOPACKET_SELECT_REL = (
    "subject",
    "meta_data",
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
                prefetch_related(*PHENOPACKET_PREFETCH).select_related(*PHENOPACKET_SELECT_REL).order_by("id")
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
    queryset = m.GenomicInterpretation.objects.all().order_by("id")
    serializer_class = s.GenomicInterpretationSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.GenomicInterpretationFilter


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
