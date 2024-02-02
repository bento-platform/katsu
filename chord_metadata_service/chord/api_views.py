import json
import logging

from asgiref.sync import async_to_sync, sync_to_async

from rest_framework import status, viewsets
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.decorators import action

from django_filters.rest_framework import DjangoFilterBackend
from chord_metadata_service.cleanup.run_all import run_all_cleanup

from chord_metadata_service.resources.serializers import ResourceSerializer
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
    def dats(self, _request, *_args, **_kwargs):
        """
        Retrieve a specific DATS file for a given dataset.

        Return the DATS file as a JSON response or an error if not found.
        """
        dataset = self.get_object()
        return Response(dataset.dats_file)

    @action(detail=True, methods=["get"])
    def resources(self, _request, *_args, **_kwargs):
        """
        Retrieve all resources (phenopackets/additional_resources) for a dataset and return a JSON response serialized
        using ResourceSerializer
        """
        dataset = self.get_object()
        return Response(ResourceSerializer(dataset.resources.all(), many=True).data)

    @async_to_sync
    async def destroy(self, request, *args, **kwargs):
        get_obj_async = sync_to_async(self.get_object)

        dataset = await get_obj_async()
        await dataset.adelete()

        logger.info(f"Running cleanup after deleting dataset {dataset.identifier} via DRF API")
        n_removed = await run_all_cleanup()
        logger.info(f"Cleanup: removed {n_removed} objects in total")
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _parse_dats(self, request) -> str | None:
        dats_file = request.data.get('dats_file')
        if isinstance(dats_file, str):
            try:
                dats_file = json.loads(dats_file)
            except json.JSONDecodeError:
                error_msg = ("Submitted dataset.dats_file data is not a valid JSON string. "
                             "Make sure the string value is JSON compatible, or submit dats_file as a JSON object.")
                logger.error(error_msg)
                return error_msg
            # Set dats_file request value to JSON
            request.data['dats_file'] = dats_file

    def create(self, request, *args, **kwargs):
        """
        Creates a Dataset.
        If the request's dats_file is a string, it will be parsed to JSON.
        """
        if error_msg := self._parse_dats(request):
            return Response(error_msg, status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if error_msg := self._parse_dats(request):
            return Response(error_msg, status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)


class ProjectJsonSchemaViewSet(CHORDPublicModelViewSet):
    """
    get:
    Return list of ProjectJsonSchema

    post:
    Create a new ProjectJsonSchema
    """

    queryset = ProjectJsonSchema.objects.all().order_by("project_id")
    serializer_class = ProjectJsonSchemaSerializer
