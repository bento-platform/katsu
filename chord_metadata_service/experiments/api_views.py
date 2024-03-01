from asgiref.sync import async_to_sync
from bento_lib.auth.permissions import P_QUERY_DATA
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.authz.permissions import BentoAllowAny
from chord_metadata_service.chord.data_types import DATA_TYPE_EXPERIMENT
from chord_metadata_service.discovery.helpers import datasets_allowed_for_request_and_data_type
from chord_metadata_service.restapi.api_renderers import (
    FHIRRenderer,
    PhenopacketsRenderer,
    ExperimentCSVRenderer,
)
from chord_metadata_service.restapi.constants import MODEL_ID_PATTERN
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination, BatchResultsSetPagination
from chord_metadata_service.restapi.negociation import FormatInPostContentNegotiation

from .serializers import ExperimentSerializer, ExperimentResultSerializer
from .models import Experiment, ExperimentResult
from .schemas import EXPERIMENT_SCHEMA
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


class ExperimentViewSet(viewsets.ModelViewSet):
    """
    get:
    Return a list of all existing experiments

    post:
    Create a new experiment
    """

    serializer_class = ExperimentSerializer
    pagination_class = LargeResultsSetPagination
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    filter_backends = [DjangoFilterBackend]
    filterset_class = ExperimentFilter
    lookup_value_regex = MODEL_ID_PATTERN

    @async_to_sync
    async def get_queryset(self):
        return (
            Experiment.objects
            .filter(dataset_id__in=await datasets_allowed_for_request_and_data_type(self.request, DATA_TYPE_EXPERIMENT))
            .select_related(*EXPERIMENT_SELECT_REL)
            .prefetch_related(*EXPERIMENT_PREFETCH)
            .order_by("id")
        )

    def list(self, request, *args, **kwargs):
        authz_middleware.mark_authz_done(self.request)  # done in get_queryset()
        return super().list(request, *args, **kwargs)


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
    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, FHIRRenderer,
                        PhenopacketsRenderer, ExperimentCSVRenderer)
    content_negotiation_class = FormatInPostContentNegotiation

    @async_to_sync
    async def get_queryset(self):
        # It's ok to allow public querying by ID here, since it doesn't give any feedback to the user whether
        # an experiment they're not allowed to access is present or not based on ID.
        experiment_ids = self.request.data.get("id", None)
        return (
            Experiment.objects
            .filter(
                dataset_id__in=await datasets_allowed_for_request_and_data_type(
                    self.request,
                    DATA_TYPE_EXPERIMENT,
                    # If we're POSTing, we are actually querying still, not creating - so override this with query:data
                    permission_override=P_QUERY_DATA if self.request.method == "POST" else None,
                ),
                **({"id__in": experiment_ids} if experiment_ids else {}),
            )
            .select_related(*EXPERIMENT_SELECT_REL)
            .prefetch_related(*EXPERIMENT_PREFETCH)
            .order_by("id")
        )

    def list(self, request, *args, **kwargs):
        authz_middleware.mark_authz_done(request)
        return super().list(request, *args, **kwargs)

    def create(self, request, *_args, **_kwargs):  # overrides POST, not actually creating anything
        # ids_list = request.data.get('id', [])
        # request.data["id"] = ids_list
        queryset = self.get_queryset()  # this itself gets the ID list from request data
        authz_middleware.mark_authz_done(request)
        return Response(ExperimentSerializer(queryset, many=True).data, status=status.HTTP_200_OK)


class ExperimentResultViewSet(viewsets.ModelViewSet):
    """
    get:
    Return a list of all existing experiment results

    post:
    Create a new experiment result
    """

    serializer_class = ExperimentResultSerializer
    pagination_class = LargeResultsSetPagination
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    filter_backends = [DjangoFilterBackend]
    filterset_class = ExperimentResultFilter

    @async_to_sync
    async def get_queryset(self):
        # Limit datasets to the intersection of datasets they request & datasets they're actually allowed to access.

        # It's ok to allow public querying by ID here, since it doesn't give any feedback to the user whether
        # a dataset they're not allowed to access is present or not based on ID
        # – they know it either doesn't exist or they don't have permission to access it, but not which case between
        #   these two.

        dataset_ids = set(self.request.get("datasets", [])) & set(
            await datasets_allowed_for_request_and_data_type(self.request, DATA_TYPE_EXPERIMENT))

        filter_by_dataset = {"experiment_set__dataset_id__in": dataset_ids} if dataset_ids else {}
        return ExperimentResult.objects.filter(**filter_by_dataset).order_by("id")

    # Cache page for the requested url for 2 hours
    def dispatch(self, *args, **kwargs):
        return super(ExperimentResultViewSet, self).dispatch(*args, **kwargs)

    def list(self, request, *args, **kwargs):
        authz_middleware.mark_authz_done(request)  # get_queryset has done the permissions logic already
        return super().list(request, *args, **kwargs)


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
    return Response(EXPERIMENT_SCHEMA)
