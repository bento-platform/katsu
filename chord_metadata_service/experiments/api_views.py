from asgiref.sync import async_to_sync
from bento_lib.auth.permissions import P_QUERY_DATA
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.settings import api_settings
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response

from chord_metadata_service.authz.permissions import BentoAllowAny
from chord_metadata_service.authz.viewset import BentoAuthzScopedModelViewSet, BentoAuthzScopedModelGenericListViewSet
from chord_metadata_service.chord.data_types import DATA_TYPE_EXPERIMENT
from chord_metadata_service.discovery.scope import get_request_discovery_scope
from chord_metadata_service.restapi.api_renderers import (
    PhenopacketsRenderer,
    ExperimentCSVRenderer,
    ExperimentResultCSVRenderer,
    ExperimentResultXLSXRenderer,
    ExperimentResultManifestTSVRenderer,
    csv_fields_error_response,
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
    "experiment_results__experiments__dataset",
    "biosample__individual"
)


class ExperimentViewSet(BentoAuthzScopedModelViewSet):
    """
    get:
    Return a list of all existing experiments

    post:
    Create a new experiment
    """

    data_type = DATA_TYPE_EXPERIMENT

    serializer_class = ExperimentSerializer
    pagination_class = LargeResultsSetPagination
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    filter_backends = [DjangoFilterBackend]
    filterset_class = ExperimentFilter
    lookup_value_regex = MODEL_ID_PATTERN

    @async_to_sync
    async def get_queryset(self):
        return (
            Experiment
            .get_model_scoped_queryset(await get_request_discovery_scope(self.request))
            .select_related(*EXPERIMENT_SELECT_REL)
            .prefetch_related(*EXPERIMENT_PREFETCH)
            .order_by("id")
        )


class ExperimentBatchViewSet(BentoAuthzScopedModelGenericListViewSet):
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

    data_type = DATA_TYPE_EXPERIMENT

    async def _filtered_queryset(self, ids_list: list[str] | None = None):
        # We pre-filter experiments to the scope. This way, if they specify an ID outside the scope, it's just ignored
        #  - the requester won't even know if it exists.
        queryset = Experiment.get_model_scoped_queryset(await get_request_discovery_scope(self.request))

        if ids_list:
            queryset = queryset.filter(id__in=ids_list)

        return queryset.select_related(*EXPERIMENT_SELECT_REL).prefetch_related(*EXPERIMENT_PREFETCH).order_by("id")

    @async_to_sync
    async def _get_filtered_queryset(self, ids_list: list[str] | None = None):
        return await self._filtered_queryset(ids_list)

    @async_to_sync
    async def get_queryset(self):
        # Note: cannot call self._get_filtered_queryset(...) here - it is itself wrapped in async_to_sync, and calling
        # an async_to_sync-wrapped callable from within an already-running event loop (as we are here) raises a
        # RuntimeError, so we call the underlying async method directly instead.
        return await self._filtered_queryset(self.request.data.get("id", None))

    def permission_from_request(self, request: DrfRequest):
        if self.action in ("list", "create", "export_fields"):
            # Here, "create" maps to the data query permission because we use create(..) (i.e., POST) as a way to run a
            # query with a large body.
            # TODO: distant future: replace with HTTP QUERY verb.
            return P_QUERY_DATA
        return None  # viewset not implemented for any other action

    def list(self, request, *args, **kwargs):
        if (err := csv_fields_error_response(request, ExperimentCSVRenderer)) is not None:
            return err
        return super().list(request, *args, **kwargs)

    def create(self, request, *_args, **_kwargs):
        """
        Despite the name, this is a POST request for returning a list of experiments. Since query parameters have a
        maximum size, POST requests can be used for large batches.
        """
        if (err := csv_fields_error_response(request, ExperimentCSVRenderer)) is not None:
            return err

        queryset = self._get_filtered_queryset(request.data.get("id", []))
        serializer = ExperimentSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def export_fields(self, _request: DrfRequest, *_args, **_kwargs):
        return Response(ExperimentCSVRenderer.field_choices())


class ExperimentResultViewSet(BentoAuthzScopedModelViewSet):
    """
    get:
    Return a list of all existing experiment results

    post:
    Create a new experiment result
    """

    data_type = DATA_TYPE_EXPERIMENT

    serializer_class = ExperimentResultSerializer
    pagination_class = LargeResultsSetPagination
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    filter_backends = [DjangoFilterBackend]
    filterset_class = ExperimentResultFilter

    @async_to_sync
    async def get_queryset(self):
        return (
            ExperimentResult
            .get_model_scoped_queryset(await get_request_discovery_scope(self.request))
            .order_by("id")
        )


class ExperimentResultBatchViewSet(BentoAuthzScopedModelGenericListViewSet):
    """
    get:
    Return a list of all existing experiment results

    post:
    return a list of experiment results based on a list of ids
    """

    serializer_class = ExperimentResultSerializer
    pagination_class = BatchResultsSetPagination
    renderer_classes = (
        *api_settings.DEFAULT_RENDERER_CLASSES,
        PhenopacketsRenderer,
        ExperimentResultCSVRenderer,
        ExperimentResultXLSXRenderer,
        ExperimentResultManifestTSVRenderer,
    )
    content_negotiation_class = FormatInPostContentNegotiation

    data_type = DATA_TYPE_EXPERIMENT

    async def _filtered_queryset(self, ids_list: list[str] | None = None):
        # We pre-filter experiment results to the scope. This way, if they specify an ID outside the scope, it's
        # just ignored - the requester won't even know if it exists.
        queryset = ExperimentResult.get_model_scoped_queryset(await get_request_discovery_scope(self.request))

        if ids_list:
            queryset = queryset.filter(id__in=ids_list)

        return queryset.order_by("id")

    @async_to_sync
    async def _get_filtered_queryset(self, ids_list: list[str] | None = None):
        return await self._filtered_queryset(ids_list)

    @async_to_sync
    async def get_queryset(self):
        # Note: cannot call self._get_filtered_queryset(...) here - it is itself wrapped in async_to_sync, and calling
        # an async_to_sync-wrapped callable from within an already-running event loop (as we are here) raises a
        # RuntimeError, so we call the underlying async method directly instead.
        return await self._filtered_queryset(self.request.data.get("id", None))

    def permission_from_request(self, request: DrfRequest):
        if self.action in ("list", "create", "export_fields"):
            # Here, "create" maps to the data query permission because we use create(..) (i.e., POST) as a way to run a
            # query with a large body.
            # TODO: distant future: replace with HTTP QUERY verb.
            return P_QUERY_DATA
        return None  # viewset not implemented for any other action

    def list(self, request, *args, **kwargs):
        if (err := csv_fields_error_response(request, ExperimentResultCSVRenderer)) is not None:
            return err
        return super().list(request, *args, **kwargs)

    def create(self, request, *_args, **_kwargs):
        """
        Despite the name, this is a POST request for returning a list of experiment results. Since query parameters
        have a maximum size, POST requests can be used for large batches.
        """
        if (err := csv_fields_error_response(request, ExperimentResultCSVRenderer)) is not None:
            return err

        queryset = self._get_filtered_queryset(request.data.get("id", []))
        serializer = ExperimentResultSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def export_fields(self, _request: DrfRequest, *_args, **_kwargs):
        return Response(ExperimentResultCSVRenderer.field_choices())


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
