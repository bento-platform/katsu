from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from chord_metadata_service.authz.permissions import BentoAllowAny
from chord_metadata_service.restapi.api_renderers import (
    PhenopacketsRenderer,
    BiosamplesCSVRenderer,
    IndividualBentoSearchRenderer,
)
from chord_metadata_service.restapi.constants import MODEL_ID_PATTERN
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination, BatchResultsSetPagination
from chord_metadata_service.restapi.negociation import FormatInPostContentNegotiation
from chord_metadata_service.phenopackets.schemas import PHENOPACKET_SCHEMA, phenopacket_resolver, phenopacket_base_uri
from . import models as m, serializers as s, filters as f
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status


class PhenopacketsModelViewSet(viewsets.ModelViewSet):
    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, PhenopacketsRenderer)
    pagination_class = LargeResultsSetPagination


BIOSAMPLE_PREFETCH = (
    "phenotypic_features",
    "experiment_set",
)


class BiosampleViewSet(PhenopacketsModelViewSet):
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


class BiosampleBatchViewSet(PhenopacketsModelViewSet):
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
    renderer_classes = (
        *api_settings.DEFAULT_RENDERER_CLASSES,
        PhenopacketsRenderer,
        BiosamplesCSVRenderer,
        IndividualBentoSearchRenderer,
    )
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
    "meta_data__resources",
    "phenotypic_features",
    "subject",
    "interpretations",
)

PHENOPACKET_SELECT_REL = (
    "subject",
    "meta_data",
)


class PhenopacketViewSet(PhenopacketsModelViewSet):
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
    lookup_value_regex = MODEL_ID_PATTERN


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
    # TODO: project-scope
    return Response(PHENOPACKET_SCHEMA)


@api_view(["GET"])
@permission_classes([BentoAllowAny])
def get_chord_phenopacket_subschema(_request, subschema: str):
    """
    get:
    Chord phenopacket schema that can be shared with data providers.
    """
    # TODO: project-scope
    schema = phenopacket_resolver.lookup(ref=f"{phenopacket_base_uri}/{subschema}").contents
    return Response(schema)
