from asgiref.sync import async_to_sync
from bento_lib.auth.permissions import P_QUERY_DATA
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response

from chord_metadata_service.authz.permissions import BentoAllowAny
from chord_metadata_service.authz.viewset import BentoAuthzScopedModelViewSet, BentoAuthzScopedModelGenericListViewSet
from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET
from chord_metadata_service.discovery.scope import get_request_discovery_scope
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


class PhenopacketsModelViewSet(BentoAuthzScopedModelViewSet):
    data_type = DATA_TYPE_PHENOPACKET

    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, PhenopacketsRenderer)
    pagination_class = LargeResultsSetPagination


BIOSAMPLE_PREFETCH = (
    "phenotypic_features",
    "experiment_set",
    "experiment_set__experiment_results",
    "experiment_set__instrument",
)

BIOSAMPLE_SELECT_REL = (
    "individual",
    "derived_from_id",
    "location_collected",
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
    lookup_value_regex = MODEL_ID_PATTERN

    # required to have discovery-scope-enabled queryset here to use a BentoAuthzScopedModelViewSet-derived viewset
    @async_to_sync
    async def get_queryset(self):
        return (
            m.Biosample.get_model_scoped_queryset(await get_request_discovery_scope(self.request))
            .prefetch_related(*BIOSAMPLE_PREFETCH)
            .select_related(*BIOSAMPLE_SELECT_REL)
            .order_by("id")
        )


class BiosampleBatchViewSet(BentoAuthzScopedModelGenericListViewSet):
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

    data_type = DATA_TYPE_PHENOPACKET

    @async_to_sync
    async def _get_filtered_queryset(self, ids_list: list[str] | None = None):
        # We pre-filter biosamples to the scope. This way, if they specify an ID outside the scope, it's just ignored
        #  - the requester won't even know if it exists.
        queryset = m.Biosample.get_model_scoped_queryset(await get_request_discovery_scope(self.request))

        if ids_list:
            queryset = queryset.filter(id__in=ids_list)

        return queryset.prefetch_related(*BIOSAMPLE_PREFETCH).select_related(*BIOSAMPLE_SELECT_REL).order_by("id")

    def get_queryset(self):
        return self._get_filtered_queryset(ids_list=self.request.data.get("id", None))

    def permission_from_request(self, request: DrfRequest):
        if self.action in ("list", "create"):
            # Here, "create" maps to the data query permission because we use create(..) (i.e., POST) as a way to run a
            # query with a large body.
            return P_QUERY_DATA
        return None  # viewset not implemented for any other action

    def create(self, request, *args, **kwargs):
        """
        Despite the name, this is a POST request for returning a list of biosamples. Since query parameters have a
        maximum size, POST requests can be used for large batches.
        """

        queryset = self._get_filtered_queryset(ids_list=request.data.get("id", []))

        serializer = s.BiosampleSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


PHENOPACKET_PREFETCH = (
    *(f"biosamples__{p}" for p in BIOSAMPLE_PREFETCH),
    "meta_data__resources",
    "diseases",
    "phenotypic_features",
    "interpretations",
    "interpretations__diagnosis__genomic_interpretations",
)

PHENOPACKET_SELECT_REL = (
    *(f"biosamples__{p}" for p in BIOSAMPLE_SELECT_REL),
    "interpretations__diagnosis",
    "interpretations__diagnosis__genomic_interpretations__biosample",
    "interpretations__diagnosis__genomic_interpretations__subject",
    "interpretations__diagnosis__genomic_interpretations__gene_descriptor",
    "interpretations__diagnosis__genomic_interpretations__variant_interpretation__variation_descriptor",
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
    lookup_value_regex = MODEL_ID_PATTERN

    # required to have discovery-scope-enabled queryset here to use a BentoAuthzScopedModelViewSet-derived viewset
    @async_to_sync
    async def get_queryset(self):
        return (
            m.Phenopacket.get_model_scoped_queryset(await get_request_discovery_scope(self.request))
            .prefetch_related(*PHENOPACKET_PREFETCH)
            .select_related(*PHENOPACKET_SELECT_REL)
            .order_by("id")
        )


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
