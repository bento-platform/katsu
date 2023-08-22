import logging
import json

from rest_framework import status, viewsets
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.decorators import action

from django_filters.rest_framework import DjangoFilterBackend
from chord_metadata_service.cleanup.run_all import run_all_cleanup

from chord_metadata_service.restapi.api_renderers import PhenopacketsRenderer, JSONLDDatasetRenderer, RDFDatasetRenderer
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination

from .models import Project, Dataset, ProjectJsonSchema
from .permissions import OverrideOrSuperUserOnly
from .serializers import (
    ProjectJsonSchemaSerializer,
    ProjectSerializer,
    DatasetSerializer
)
from .filters import AuthorizedDatasetFilter

logger = logging.getLogger(__name__)


__all__ = ["ProjectViewSet", "DatasetViewSet"]


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class CHORDModelViewSet(viewsets.ModelViewSet):
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (PhenopacketsRenderer,)
    pagination_class = LargeResultsSetPagination
    permission_classes = [OverrideOrSuperUserOnly]  # Explicit


class CHORDPublicModelViewSet(CHORDModelViewSet):
    permission_classes = [OverrideOrSuperUserOnly | ReadOnly]


class ProjectViewSet(CHORDPublicModelViewSet):
    """
    get:
    Return a list of all existing projects

    post:
    Create a new project
    """

    queryset = Project.objects.all().order_by("identifier")
    serializer_class = ProjectSerializer


class DatasetViewSet(CHORDPublicModelViewSet):
    """
    get:
    Return a list of all existing datasets

    post:
    Create a new dataset
    """

    filter_backends = [DjangoFilterBackend]
    filterset_class = AuthorizedDatasetFilter
    lookup_url_kwarg = "dataset_id"

    serializer_class = DatasetSerializer
    renderer_classes = tuple(CHORDModelViewSet.renderer_classes) + (JSONLDDatasetRenderer, RDFDatasetRenderer,)
    queryset = Dataset.objects.all().order_by("title")

    @action(detail=True, methods=['get'])
    def dats(self, request, pk=None):
        """
        Retrieve a specific DATS file for a given dataset.

        Return the DATS file as a JSON response or an error if not found.
        """
        dataset = self.get_object()
        return Response(json.loads(dataset.dats_file))

    def destroy(self, request, *args, **kwargs):
        dataset = self.get_object()
        dataset.delete()

        logger.info(f"Running cleanup after deleting dataset {dataset.identifier} via DRF API")
        n_removed = run_all_cleanup()
        logger.info(f"Cleanup: removed {n_removed} objects in total")
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectJsonSchemaViewSet(CHORDPublicModelViewSet):
    """
    get:
    Return list of ProjectJsonSchema

    post:
    Create a new ProjectJsonSchema
    """

    queryset = ProjectJsonSchema.objects.all().order_by("project_id")
    serializer_class = ProjectJsonSchemaSerializer
