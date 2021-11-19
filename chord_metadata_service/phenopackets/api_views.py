from django.conf import settings
from rest_framework import viewsets
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend

from chord_metadata_service.restapi.api_renderers import PhenopacketsRenderer, FHIRRenderer
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination
from chord_metadata_service.phenopackets.schemas import PHENOPACKET_SCHEMA
from . import models as m, serializers as s, filters as f


class PhenopacketsModelViewSet(viewsets.ModelViewSet):
    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, PhenopacketsRenderer)
    pagination_class = LargeResultsSetPagination

    # Cache page for the requested url for 2 hours
    @method_decorator(cache_page(settings.CACHE_TIME))
    def dispatch(self, *args, **kwargs):
        return super(PhenopacketsModelViewSet, self).dispatch(*args, **kwargs)


class ExtendedPhenopacketsModelViewSet(PhenopacketsModelViewSet):
    renderer_classes = (*PhenopacketsModelViewSet.renderer_classes, FHIRRenderer)


class PhenotypicFeatureViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing phenotypic features

    post:
    Create a new phenotypic feature

    """
    queryset = m.PhenotypicFeature.objects.all().order_by("id")
    serializer_class = s.PhenotypicFeatureSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.PhenotypicFeatureFilter


class ProcedureViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing procedures

    post:
    Create a new procedure

    """
    queryset = m.Procedure.objects.all().order_by("id")
    serializer_class = s.ProcedureSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.ProcedureFilter


class HtsFileViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing HTS files

    post:
    Create a new HTS file

    """
    queryset = m.HtsFile.objects.all().order_by("uri")
    serializer_class = s.HtsFileSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.HtsFileFilter


class GeneViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing genes

    post:
    Create a new gene

    """
    queryset = m.Gene.objects.all().order_by("id")
    serializer_class = s.GeneSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.GeneFilter


class VariantViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing variants

    post:
    Create a new variant

    """
    queryset = m.Variant.objects.all().order_by("id")
    serializer_class = s.VariantSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.VariantFilter


class DiseaseViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing diseases

    post:
    Create a new disease

    """
    queryset = m.Disease.objects.all().order_by("id")
    serializer_class = s.DiseaseSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.DiseaseFilter


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
    queryset = m.MetaData.objects.all().prefetch_related(*META_DATA_PREFETCH).order_by("id")
    serializer_class = s.MetaDataSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.MetaDataFilter


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
    queryset = m.Biosample.objects.all() \
        .prefetch_related(*BIOSAMPLE_PREFETCH) \
        .select_related(*BIOSAMPLE_SELECT_REL) \
        .order_by("id")
    serializer_class = s.BiosampleSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.BiosampleFilter


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
    queryset = m.Phenopacket.objects.all()\
        .prefetch_related(*PHENOPACKET_PREFETCH)\
        .select_related(*PHENOPACKET_SELECT_REL)\
        .order_by("id")
    serializer_class = s.PhenopacketSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.PhenopacketFilter


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
    queryset = m.Diagnosis.objects.all().order_by("id")
    serializer_class = s.DiagnosisSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.DiagnosisFilter


class InterpretationViewSet(PhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing interpretations

    post:
    Create a new interpretation

    """
    queryset = m.Interpretation.objects.all().order_by("id")
    serializer_class = s.InterpretationSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.InterpretationFilter


@api_view(["GET"])
@permission_classes([AllowAny])
def get_chord_phenopacket_schema(_request):
    """
    get:
    Chord phenopacket schema that can be shared with data providers.
    """
    return Response(PHENOPACKET_SCHEMA)
