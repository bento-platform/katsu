from asgiref.sync import async_to_sync
from bento_lib.auth.permissions import P_QUERY_DATA
from bento_lib.responses import errors
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status, viewsets
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.authz.permissions import BentoPhenopacketDataPermission, BentoAllowAny
from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET
from chord_metadata_service.discovery.scope import get_request_discovery_scope
from chord_metadata_service.restapi.api_renderers import (
    PhenopacketsRenderer,
    FHIRRenderer,
    BiosamplesCSVRenderer,
    IndividualBentoSearchRenderer,
)
from chord_metadata_service.restapi.constants import MODEL_ID_PATTERN
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination, BatchResultsSetPagination
from chord_metadata_service.restapi.negociation import FormatInPostContentNegotiation
from chord_metadata_service.phenopackets.schemas import PHENOPACKET_SCHEMA, phenopacket_resolver, phenopacket_base_uri

from . import models as m, serializers as s, filters as f


class PhenopacketsModelViewSet(viewsets.ModelViewSet):
    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, PhenopacketsRenderer)
    pagination_class = LargeResultsSetPagination
    permission_classes = (BentoPhenopacketDataPermission,)


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
    lookup_value_regex = MODEL_ID_PATTERN

    # We scope the queryset according to requested discovery scope below, which lets us have more fine-grained
    # permissions.
    scope_enabled = True

    @async_to_sync
    async def get_queryset(self):
        return (
            m.Biosample.get_model_scoped_queryset(await get_request_discovery_scope(self.request))
            .prefetch_related(*BIOSAMPLE_PREFETCH)
            .order_by("id")
        )


class BiosampleBatchViewSet(viewsets.ModelViewSet):
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
        FHIRRenderer,
        PhenopacketsRenderer,
        BiosamplesCSVRenderer,
        IndividualBentoSearchRenderer,
    )
    content_negotiation_class = FormatInPostContentNegotiation

    # We scope the queryset according to requested discovery scope below, which lets us have more fine-grained
    # permissions.
    scope_enabled = True

    # TODO: this shouldn't be its own separate viewset maybe...

    @async_to_sync
    async def _get_filtered_queryset(self, ids_list: list[str] | None = None):
        # We pre-filter biosamples to the scope. This way, if they specify an ID outside the scope, it's just ignored
        #  - the requester won't even know if it exists.
        queryset = m.Biosample.get_model_scoped_queryset(await get_request_discovery_scope(self.request))

        if ids_list:
            queryset = queryset.filter(id__in=ids_list)

        return queryset.prefetch_related(*BIOSAMPLE_PREFETCH).order_by("id")

    def get_queryset(self):
        return self._get_filtered_queryset(ids_list=self.request.data.get("id", None))

    @async_to_sync
    async def check_batch_permissions(self, request):
        scope = await get_request_discovery_scope(request)
        return await authz_middleware.async_evaluate_one(
            request, scope.as_authz_resource(data_type=DATA_TYPE_PHENOPACKET), P_QUERY_DATA, mark_authz_done=True
        )

    def create(self, request, *args, **kwargs):
        """
        Despite the name, this is a POST request for returning a list of biosamples. Since query parameters have a
        maximum size, POST requests can be used for large batches.
        """

        if not self.check_batch_permissions(request):
            return Response(errors.forbidden_error(), status=status.HTTP_403_FORBIDDEN)

        queryset = self._get_filtered_queryset(ids_list=request.data.get("id", []))

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

    # We scope the queryset according to requested discovery scope below, which lets us have more fine-grained
    # permissions.
    scope_enabled = True

    @async_to_sync
    async def get_queryset(self):
        return (
            m.Phenopacket.get_model_scoped_queryset(await get_request_discovery_scope(self.request))
            .prefetch_related(*PHENOPACKET_PREFETCH)
            .order_by("id")
        )


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
