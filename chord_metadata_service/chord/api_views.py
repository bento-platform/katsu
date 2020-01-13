from rest_framework import viewsets
from chord_metadata_service.phenopackets.api_views import LargeResultsSetPagination
from .models import *
from .serializers import *
from chord_metadata_service.restapi.api_renderers import PhenopacketsRenderer
from rest_framework.settings import api_settings


__all__ = ["ProjectViewSet", "DatasetViewSet", "TableOwnershipViewSet"]


class PhenopacketsModelViewSet(viewsets.ModelViewSet):
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (PhenopacketsRenderer,)
    pagination_class = LargeResultsSetPagination


class ProjectViewSet(PhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing projects

    post:
    Create a new project
    """

    queryset = Project.objects.all().order_by("identifier")
    serializer_class = ProjectSerializer


class DatasetViewSet(PhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing datasets

    post:
    Create a new dataset
    """

    queryset = Dataset.objects.all().order_by("identifier")
    serializer_class = DatasetSerializer


class TableOwnershipViewSet(PhenopacketsModelViewSet):
    """
    get:
    Return a list of table-(dataset|dataset,biosample) relationships

    post:
    Create a new relationship between a dataset (and optionally a specific biosample) and a table
    in another service
    """

    queryset = TableOwnership.objects.all().order_by("table_id")
    serializer_class = TableOwnershipSerializer
