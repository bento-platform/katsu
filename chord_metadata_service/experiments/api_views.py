from rest_framework import viewsets
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import ExperimentSerializer, ExperimentResultSerializer
from .models import Experiment, ExperimentResult
from .schemas import EXPERIMENT_SCHEMA
from .filters import ExperimentFilter, ExperimentResultFilter
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

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
)


class ExperimentViewSet(viewsets.ModelViewSet):
    """
    get:
    Return a list of all existing experiments

    post:
    Create a new experiment
    """

    queryset = Experiment.objects.all() \
        .select_related(*EXPERIMENT_SELECT_REL) \
        .prefetch_related(*EXPERIMENT_PREFETCH) \
        .order_by("id")
    serializer_class = ExperimentSerializer
    pagination_class = LargeResultsSetPagination
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    filter_backends = [DjangoFilterBackend]
    filterset_class = ExperimentFilter

    def dispatch(self, *args, **kwargs):
        return super(ExperimentViewSet, self).dispatch(*args, **kwargs)


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

    # Cache page for the requested url for 2 hours
    @method_decorator(cache_page(60 * 60 * 2))
    def dispatch(self, *args, **kwargs):
        return super(ExperimentResultViewSet, self).dispatch(*args, **kwargs)


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
@permission_classes([AllowAny])
def get_experiment_schema(_request):
    """
    get:
    Experiment schema
    """
    return Response(EXPERIMENT_SCHEMA)
