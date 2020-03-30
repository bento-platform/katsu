from rest_framework import viewsets
from rest_framework.settings import api_settings
from .serializers import ExperimentSerializer
from .models import Experiment
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination


class ExperimentViewSet(viewsets.ModelViewSet):
    """
    get:
    Return a list of all existing experiments

    post:
    Create a new experiment
    """

    queryset = Experiment.objects.all().order_by("id")
    serializer_class = ExperimentSerializer
    pagination_class = LargeResultsSetPagination
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES)
