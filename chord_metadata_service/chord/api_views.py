from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from chord_metadata_service.phenopackets.api_views import LargeResultsSetPagination
from .models import *
from .serializers import *


__all__ = ["ProjectViewSet", "DatasetViewSet", "TableOwnershipViewSet"]


class ProjectViewSet(viewsets.ModelViewSet):
    """
    get:
    Return a list of all existing projects

    post:
    Create a new project
    """

    queryset = Project.objects.all().order_by("project_id")
    serializer_class = ProjectSerializer
    pagination_class = LargeResultsSetPagination

    # noinspection PyUnusedLocal
    @action(detail=True, methods=["GET"])
    def datasets(self, _request, pk):
        project = self.get_object()
        datasets = Dataset.objects.filter(project=project).order_by("dataset_id")

        page = self.paginate_queryset(datasets)
        if page is not None:
            serializer = DatasetSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = DatasetSerializer(datasets, many=True)
        return Response(serializer.data)


class DatasetViewSet(viewsets.ModelViewSet):
    """
    get:
    Return a list of all existing datasets

    post:
    Create a new dataset
    """

    queryset = Dataset.objects.all().order_by("dataset_id")
    serializer_class = DatasetSerializer
    pagination_class = LargeResultsSetPagination


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
