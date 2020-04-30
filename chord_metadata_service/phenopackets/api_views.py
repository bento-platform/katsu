from rest_framework import viewsets
from rest_framework.settings import api_settings

from chord_metadata_service.restapi.api_renderers import *
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination
from .serializers import *
from .models import *


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
    queryset = PhenotypicFeature.objects.all().order_by("id")
    serializer_class = PhenotypicFeatureSerializer


class ProcedureViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing procedures

    post:
    Create a new procedure

    """
    queryset = Procedure.objects.all().order_by("id")
    serializer_class = ProcedureSerializer


class HtsFileViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing HTS files

    post:
    Create a new HTS file

    """
    queryset = HtsFile.objects.all().order_by("uri")
    serializer_class = HtsFileSerializer


class GeneViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing genes

    post:
    Create a new gene

    """
    queryset = Gene.objects.all().order_by("id")
    serializer_class = GeneSerializer


class VariantViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing variants

    post:
    Create a new variant

    """
    queryset = Variant.objects.all().order_by("id")
    serializer_class = VariantSerializer


class DiseaseViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing diseases

    post:
    Create a new disease

    """
    queryset = Disease.objects.all().order_by("id")
    serializer_class = DiseaseSerializer


class ResourceViewSet(PhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing resources

    post:
    Create a new resource

    """
    queryset = Resource.objects.all().order_by("id")
    serializer_class = ResourceSerializer


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
    queryset = MetaData.objects.all().prefetch_related(*META_DATA_PREFETCH).order_by("id")
    serializer_class = MetaDataSerializer


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
    queryset = Biosample.objects.all().prefetch_related(*BIOSAMPLE_PREFETCH).order_by("id")
    serializer_class = BiosampleSerializer


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
    queryset = Phenopacket.objects.all().prefetch_related(*PHENOPACKET_PREFETCH).order_by("id")
    serializer_class = PhenopacketSerializer


class GenomicInterpretationViewSet(PhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing genomic interpretations

    post:
    Create a new genomic interpretation

    """
    queryset = GenomicInterpretation.objects.all().order_by("id")
    serializer_class = GenomicInterpretationSerializer


class DiagnosisViewSet(PhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing diagnoses

    post:
    Create a new diagnosis

    """
    queryset = Diagnosis.objects.all().order_by("id")
    serializer_class = DiagnosisSerializer


class InterpretationViewSet(PhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing interpretations

    post:
    Create a new interpretation

    """
    queryset = Interpretation.objects.all().order_by("id")
    serializer_class = InterpretationSerializer
