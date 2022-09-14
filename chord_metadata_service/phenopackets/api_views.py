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
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers


class PhenopacketsModelViewSet(viewsets.ModelViewSet):
    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, PhenopacketsRenderer)
    pagination_class = LargeResultsSetPagination

    # Cache response to the requested URL, default to 2 hours.
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
    serializer_class = s.PhenotypicFeatureSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = f.PhenotypicFeatureFilter
    queryset = m.PhenotypicFeature.objects.all().order_by("id")


class ProcedureViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing procedures

    post:
    Create a new procedure

    """
    serializer_class = s.ProcedureSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = f.ProcedureFilter
    queryset = m.Procedure.objects.all().order_by("id")


class HtsFileViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing HTS files

    post:
    Create a new HTS file

    """
    serializer_class = s.HtsFileSerializer
    filter_backends = [DjangoFilterBackend]
    queryset = m.HtsFile.objects.all().order_by("uri")


class GeneViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing genes

    post:
    Create a new gene

    """
    serializer_class = s.GeneSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = f.GeneFilter
    queryset = m.Gene.objects.all().order_by("id")


class VariantViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing variants

    post:
    Create a new variant

    """
    serializer_class = s.VariantSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = f.VariantFilter
    queryset = m.Variant.objects.all().order_by("id")


class DiseaseViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing diseases

    post:
    Create a new disease

    """
    serializer_class = s.DiseaseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = f.DiseaseFilter
    queryset = m.Disease.objects.all().order_by("id")


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
    filterset_class = f.MetaDataFilter
    queryset = m.MetaData.objects.all().prefetch_related(*META_DATA_PREFETCH).order_by("id")


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
    filterset_class = f.BiosampleFilter
    queryset = m.Biosample.objects.all().prefetch_related(*BIOSAMPLE_PREFETCH).order_by("id")


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
    filterset_class = f.PhenopacketFilter
    queryset = m.Phenopacket.objects.all().prefetch_related(*PHENOPACKET_PREFETCH).order_by("id")


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
    filterset_class = f.GenomicInterpretationFilter


class DiagnosisViewSet(PhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing diagnoses

    post:
    Create a new diagnosis

    """
    serializer_class = s.DiagnosisSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = f.DiagnosisFilter
    queryset = m.Diagnosis.objects.all().order_by("id")


class InterpretationViewSet(PhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing interpretations

    post:
    Create a new interpretation

    """
    serializer_class = s.InterpretationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = f.InterpretationFilter
    queryset = m.Interpretation.objects.all().order_by("id")


@extend_schema(
    description="Chord phenopacket schema that can be shared with data providers",
    responses={
        200: inline_serializer(
            name='chord_phenopacket_schema_response',
            fields={
                'PHENOPACKET_SCHEMA': serializers.JSONField(),
            }
        )
    }
)
@api_view(["GET"])
@permission_classes([AllowAny])
def get_chord_phenopacket_schema(_request):
    """
    get:
    Chord phenopacket schema that can be shared with data providers.
    """
    return Response(PHENOPACKET_SCHEMA)
