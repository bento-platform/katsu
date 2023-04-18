import logging

from rest_framework import status, viewsets
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.settings import api_settings

from django_filters.rest_framework import DjangoFilterBackend

from chord_metadata_service.cleanup import run_all_cleanup
from chord_metadata_service.restapi.api_renderers import PhenopacketsRenderer, JSONLDDatasetRenderer, RDFDatasetRenderer
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination

from .models import Project, Dataset, ProjectJsonSchema, TableOwnership, Table
from .permissions import OverrideOrSuperUserOnly
from .serializers import ProjectJsonSchemaSerializer, ProjectSerializer, DatasetSerializer, TableOwnershipSerializer, TableSerializer
from .filters import AuthorizedDatasetFilter

logger = logging.getLogger(__name__)


__all__ = ["ProjectViewSet", "DatasetViewSet", "TableOwnershipViewSet", "TableViewSet"]


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

    serializer_class = DatasetSerializer
    renderer_classes = tuple(CHORDModelViewSet.renderer_classes) + (JSONLDDatasetRenderer, RDFDatasetRenderer,)
    queryset = Dataset.objects.all().order_by("title")


class TableOwnershipViewSet(CHORDPublicModelViewSet):
    """
    get:
    Return a list of table-(dataset|dataset,biosample) relationships

    post:
    Create a new relationship between a dataset (and optionally a specific biosample) and a table
    in a data service
    """

    queryset = TableOwnership.objects.all().order_by("table_id")
    serializer_class = TableOwnershipSerializer


class TableViewSet(CHORDPublicModelViewSet):
    """
    get:
    Return a list of tables

    post:
    Create a new table
    """

    # TODO: Create TableOwnership if needed - here or model?

    queryset = Table.objects.all().prefetch_related("ownership_record").order_by("ownership_record_id")
    serializer_class = TableSerializer

    def destroy(self, request, *args, **kwargs):
        # First, delete the table record itself
        # - use the cascade from the ownership record rather than the default DRF behaviour
        table = self.get_object()
        table_id = table.ownership_record_id
        table.ownership_record.delete()
        table.delete()

        # Then, run cleanup
        logger.info(f"Running cleanup after deleting table {table_id} via DRF API")
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

    queryset = ProjectJsonSchema.objects.all().order_by("project__identifier")
    serializer_class = ProjectJsonSchemaSerializer