from asgiref.sync import async_to_sync
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from chord_metadata_service.authz.permissions import BentoAllowAny
from chord_metadata_service.authz.viewset import BentoAuthzModelViewSet
from chord_metadata_service.chord.data_types import DATA_TYPE_EXPERIMENT
from chord_metadata_service.discovery.scope import get_request_discovery_scope
from chord_metadata_service.restapi.api_renderers import (
    PhenopacketsRenderer,
    ExperimentCSVRenderer,
)
from chord_metadata_service.restapi.constants import MODEL_ID_PATTERN
from chord_metadata_service.restapi.negociation import FormatInPostContentNegotiation
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination, BatchResultsSetPagination

from .serializers import ExperimentSerializer, ExperimentResultSerializer
from .models import Experiment, ExperimentResult
from .schemas import EXPERIMENT_SCHEMA, experiment_resolver, experiment_base_uri
from .filters import ExperimentFilter, ExperimentResultFilter

__all__ = [
    "EXPERIMENT_SELECT_REL",
    "EXPERIMENT_PREFETCH",
    "ExperimentViewSet",
    "get_experiment_schema",
]


EXPERIMENT_SELECT_REL = (
    "instrument",
)

EXPERIMENT_PREFETCH = (
    "experiment_results",
    "biosample__individual"
)


class ExperimentViewSet(BentoAuthzModelViewSet):
    """
    get:
    Return a list of all existing experiments

    post:
    Create a new experiment
    """

    data_type = DATA_TYPE_EXPERIMENT
    scope_enabled = True

    serializer_class = ExperimentSerializer
    pagination_class = LargeResultsSetPagination
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    filter_backends = [DjangoFilterBackend]
    filterset_class = ExperimentFilter
    lookup_value_regex = MODEL_ID_PATTERN

    @async_to_sync
    async def get_queryset(self):
        return (
            Experiment.get_model_scoped_queryset(await get_request_discovery_scope(self.request))
            .select_related(*EXPERIMENT_SELECT_REL)
            .prefetch_related(*EXPERIMENT_PREFETCH)
            .order_by("id")
        )


class BatchViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    A viewset that only implements the 'list' action.
    To be used with the BatchListRouter which maps the POST method to .list()
    """
    pass


class ExperimentBatchViewSet(BatchViewSet):
    """
    get:
    Return a list of all existing experiments

    post:
    return a list of experiments based on a list of ids
    """

    serializer_class = ExperimentSerializer
    pagination_class = BatchResultsSetPagination
    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, PhenopacketsRenderer, ExperimentCSVRenderer)
    content_negotiation_class = FormatInPostContentNegotiation

    def get_queryset(self):
        experiment_ids = self.request.data.get("id", None)
        filter_by_id = {"id__in": experiment_ids} if experiment_ids else {}

        return (
            Experiment.objects
            .filter(**filter_by_id)
            .select_related(*EXPERIMENT_SELECT_REL)
            .prefetch_related(*EXPERIMENT_PREFETCH)
            .order_by("id")
        )

    def create(self, request, *_args, **_kwargs):
        ids_list = request.data.get('id', [])
        request.data["id"] = ids_list
        queryset = self.get_queryset()

        serializer = ExperimentSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExperimentResultViewSet(viewsets.ModelViewSet):
    """
    get:
    Return a list of all existing experiment results

    post:
    Create a new experiment result
    """

    queryset = ExperimentResult.objects.all().order_by("id")
    serializer_class = ExperimentResultSerializer
    pagination_class = LargeResultsSetPagination
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    filter_backends = [DjangoFilterBackend]
    filterset_class = ExperimentResultFilter


@extend_schema(
    description="Experiment schema",
    responses={
        200: inline_serializer(
            name='get_experiment_schema_response',
            fields={
                'EXPERIMENT_SCHEMA': serializers.JSONField(),
            }
        )
    }
)
@api_view(["GET"])
@permission_classes([BentoAllowAny])
def get_experiment_schema(_request):
    """
    get:
    Experiment schema
    """
    # TODO: project-scope
    return Response(EXPERIMENT_SCHEMA)


@api_view(["GET"])
@permission_classes([BentoAllowAny])
def get_experiment_subschema(_request, subschema: str):
    """
    get:
    Experiment sub-schema
    """
    # TODO: project-scope
    schema = experiment_resolver.lookup(ref=f"{experiment_base_uri}/{subschema}").contents
    return Response(schema)
