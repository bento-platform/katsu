from rest_framework import viewsets
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import ExperimentSerializer, ListExperimentSerializer
from .models import Experiment
from .schemas import EXPERIMENT_SCHEMA
from .filters import ExperimentFilter
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination
from django.shortcuts import get_object_or_404
from django.db.models import Count

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
    filter_class = ExperimentFilter

    # a simple not nested serializer for list view
    # def list(self, request):
    #     queryset = Experiment.objects.all()
    #     # apply filtering
    #     filtered_queryset = self.filter_queryset(queryset)
    #     # paginate
    #     paginated_queryset = self.paginate_queryset(filtered_queryset)
    #     serializer = ListExperimentSerializer(paginated_queryset, many=True)
    #     return self.get_paginated_response(serializer.data)

    # Cache page for the requested url for 2 hours
    @method_decorator(cache_page(60 * 60 * 2))
    def dispatch(self, *args, **kwargs):
        return super(ExperimentViewSet, self).dispatch(*args, **kwargs)


# for test reasons
class NewExperimentViewset(viewsets.GenericViewSet):
    queryset = Experiment.objects.all() \
        .select_related(*EXPERIMENT_SELECT_REL) \
        .prefetch_related(*EXPERIMENT_PREFETCH) \
        .order_by("id")
    pagination_class = LargeResultsSetPagination
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    filter_backends = [DjangoFilterBackend]
    filter_class = ExperimentFilter

    def list(self, request):
        queryset = Experiment.objects.all()
        # apply filtering
        filtered_queryset = self.filter_queryset(queryset)
        # paginate
        paginated_queryset = self.paginate_queryset(filtered_queryset)
        serializer = ListExperimentSerializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Experiment.objects.all()
        experiment = get_object_or_404(queryset, pk=pk)
        serializer = ExperimentSerializer(experiment)
        return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_experiment_schema(_request):
    """
    get:
    Experiment schema
    """
    return Response(EXPERIMENT_SCHEMA)


@api_view(["GET"])
@permission_classes([AllowAny])
def list_experiments(_request):
    #experiments = [serialize_experiment(experiment) for experiment in Experiment.objects.all()]
    # call values() and annotate with experiment results count
    experiments = Experiment.objects.all().values(
        "id", "study_type", "experiment_type", "experiment_ontology", "molecule",
        "molecule_ontology", "library_strategy", "library_source", "library_selection", "library_layout",
        "extraction_protocol", "reference_registry_id", "qc_flags", "biosample", "table",
        "extra_properties", "created", "updated",
    ).annotate(experiment_results=Count("experiment_results"))
    return Response(experiments)
