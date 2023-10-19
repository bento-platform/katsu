import json

from asgiref.sync import async_to_sync, sync_to_async
from bento_lib.auth.permissions import P_CREATE_DATASET, P_DELETE_DATASET
from bento_lib.auth.resources import build_resource
from bento_lib.responses import errors
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.decorators import action

from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.authz.permissions import BentoAllowAnyReadOnly, BentoDeferToHandler, OverrideOrSuperUserOnly
from chord_metadata_service.cleanup.run_all import run_all_cleanup
from chord_metadata_service.logger import logger
from chord_metadata_service.resources.serializers import ResourceSerializer
from chord_metadata_service.restapi.api_renderers import PhenopacketsRenderer, JSONLDDatasetRenderer, RDFDatasetRenderer
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination

from .models import Project, Dataset, ProjectJsonSchema
from .serializers import (
    ProjectJsonSchemaSerializer,
    ProjectSerializer,
    DatasetSerializer
)
from .filters import AuthorizedDatasetFilter


__all__ = ["ProjectViewSet", "DatasetViewSet"]


RES_FORBIDDEN = Response(errors.forbidden_error(), status=status.HTTP_403_FORBIDDEN)


def forbidden(request: Request):
    authz_middleware.mark_authz_done(request)
    return Response(errors.forbidden_error(), status=status.HTTP_403_FORBIDDEN)


class CHORDModelViewSet(viewsets.ModelViewSet):
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (PhenopacketsRenderer,)
    pagination_class = LargeResultsSetPagination
    permission_classes = [OverrideOrSuperUserOnly]  # Explicit


class CHORDPublicModelViewSet(CHORDModelViewSet):
    permission_classes = [BentoAllowAnyReadOnly | BentoDeferToHandler]


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
        return Response(json.loads(dataset.dats_file))

    @action(detail=True, methods=["get"])
    def resources(self, _request, *_args, **_kwargs):
        """
        Retrieve all resources (phenopackets/additional_resources) for a dataset and return a JSON response serialized
        using ResourceSerializer
        """

        # TODO: permissions based on dataset - resources?

        dataset = self.get_object()
        return Response(ResourceSerializer(dataset.resources.all(), many=True).data)

    async def get_obj_async(self):
        return await sync_to_async(self.get_object)()

    @async_to_sync
    async def create(self, request: Request, *args, **kwargs):
        project_id = request.data.get("project")

        if project_id is None:
            return forbidden(request)

        can_create = await authz_middleware.async_evaluate(
            request, build_resource(project=project_id), P_CREATE_DATASET)

        if not can_create:
            return forbidden(request)

        authz_middleware.mark_authz_done(request)
        return super().create(request, *args, **kwargs)

    @async_to_sync
    async def destroy(self, request: Request, *args, **kwargs):
        get_obj_async = sync_to_async(self.get_object)

        try:
            dataset = await get_obj_async()
        except PermissionDenied:
            return forbidden(request)

        can_delete = await authz_middleware.async_evaluate_one(
            request, build_resource(project=dataset.project_id), P_DELETE_DATASET)

        if not can_delete:
            return forbidden(request)

        await dataset.adelete()

        logger.info(f"Running cleanup after deleting dataset {dataset.identifier} via DRF API")
        n_removed = await run_all_cleanup()
        logger.info(f"Cleanup: removed {n_removed} objects in total")

        authz_middleware.mark_authz_done(request)
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
