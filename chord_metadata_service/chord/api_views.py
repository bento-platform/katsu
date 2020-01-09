from rest_framework import viewsets

from chord_metadata_service.phenopackets.api_views import LargeResultsSetPagination
from .models import *
from .permissions import OverrideOrSuperUserOnly
from .serializers import *


__all__ = ["ProjectViewSet", "DatasetViewSet", "TableOwnershipViewSet"]


class ProjectViewSet(viewsets.ModelViewSet):
    """
    get:
    Return a list of all existing projects

    post:
    Create a new project
    """

    queryset = Project.objects.all().order_by("identifier")
    serializer_class = ProjectSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [OverrideOrSuperUserOnly]  # Explicit


class DatasetViewSet(viewsets.ModelViewSet):
    """
    get:
    Return a list of all existing datasets

    post:
    Create a new dataset
    """

    queryset = Dataset.objects.all().order_by("identifier")
    serializer_class = DatasetSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [OverrideOrSuperUserOnly]  # Explicit


class TableOwnershipViewSet(viewsets.ModelViewSet):
    """
    get:
    Return a list of table-(dataset|dataset,biosample) relationships

    post:
    Create a new relationship between a dataset (and optionally a specific biosample) and a table
    in another service
    """

    queryset = TableOwnership.objects.all().order_by("table_id")
    serializer_class = TableOwnershipSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [OverrideOrSuperUserOnly]  # Explicit
