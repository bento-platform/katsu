from asgiref.sync import async_to_sync
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status, viewsets
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.authz.permissions import BentoAllowAny
from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET
from chord_metadata_service.discovery.helpers import datasets_allowed_for_request_and_data_type
from chord_metadata_service.restapi.api_renderers import (PhenopacketsRenderer, FHIRRenderer,
                                                          BiosamplesCSVRenderer, ARGORenderer,
                                                          IndividualBentoSearchRenderer)
from chord_metadata_service.restapi.constants import MODEL_ID_PATTERN
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination, BatchResultsSetPagination
from chord_metadata_service.restapi.negociation import FormatInPostContentNegotiation
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
    filterset_class = f.PhenotypicFeatureFilter
    queryset = m.PhenotypicFeature.objects.all().order_by("id")


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
    "phenotypic_features",
    "experiment_set",
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
    filterset_class = f.BiosampleFilter
    queryset = m.Biosample.objects.all().prefetch_related(*BIOSAMPLE_PREFETCH).order_by("id")
    lookup_value_regex = MODEL_ID_PATTERN


class BiosampleBatchViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing biosamples

    post:
    Filter biosamples by a list of ids
    """
    serializer_class = s.BiosampleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = f.BiosampleFilter
    pagination_class = BatchResultsSetPagination
    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, FHIRRenderer,
                        PhenopacketsRenderer, BiosamplesCSVRenderer, ARGORenderer,
                        IndividualBentoSearchRenderer)
    content_negotiation_class = FormatInPostContentNegotiation

    def _get_filtered_queryset(self, ids_list=None):
        queryset = m.Biosample.objects.all()

        if ids_list:
            queryset = queryset.filter(id__in=ids_list)

        queryset = queryset.prefetch_related(*BIOSAMPLE_PREFETCH) \
            .order_by("id")

        return queryset

    def get_queryset(self):
        individual_ids = self.request.data.get("id", None)
        return self._get_filtered_queryset(ids_list=individual_ids)

    def create(self, request, *args, **kwargs):
        ids_list = request.data.get('id', [])
        queryset = self._get_filtered_queryset(ids_list=ids_list)

        serializer = s.BiosampleSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


PHENOPACKET_PREFETCH = (
    *(f"biosamples__{p}" for p in BIOSAMPLE_PREFETCH),
    *(f"meta_data__{p}" for p in META_DATA_PREFETCH),
    "phenotypic_features",
    "subject",
    "interpretations",
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
    lookup_value_regex = MODEL_ID_PATTERN

    @async_to_sync
    async def get_queryset(self):
        return (
            m.Phenopacket.objects
            .filter(
                dataset_id__in=await datasets_allowed_for_request_and_data_type(self.request, DATA_TYPE_PHENOPACKET))
            .prefetch_related(*PHENOPACKET_PREFETCH)
            .order_by("id")
        )

    def list(self, request, *args, **kwargs):
        authz_middleware.mark_authz_done(request)  # get_queryset has done the permissions logic already
        return super().list(request, *args, **kwargs)


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
@permission_classes([BentoAllowAny])
def get_chord_phenopacket_schema(_request):
    """
    get:
    Chord phenopacket schema that can be shared with data providers.
    """
    return Response(PHENOPACKET_SCHEMA)
