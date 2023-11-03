import json

from asgiref.sync import async_to_sync, sync_to_async
from bento_lib.auth.permissions import (
    P_CREATE_PROJECT,
    P_EDIT_PROJECT,
    P_DELETE_PROJECT,
    P_CREATE_DATASET,
    P_EDIT_DATASET,
    P_DELETE_DATASET,
)
from bento_lib.auth.resources import RESOURCE_EVERYTHING, build_resource
from bento_lib.responses import errors
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.decorators import action

from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.authz.permissions import BentoAllowAnyReadOnly, BentoDeferToHandler
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


def forbidden(request: Request):
    authz_middleware.mark_authz_done(request)
    return Response(errors.forbidden_error(), status=status.HTTP_403_FORBIDDEN)


def not_found(request: Request):
    authz_middleware.mark_authz_done(request)
    return Response(errors.not_found_error(), status=status.HTTP_404_NOT_FOUND)


class CHORDModelViewSet(viewsets.ModelViewSet):
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (PhenopacketsRenderer,)
    pagination_class = LargeResultsSetPagination

    async def get_obj_async(self):
        return await sync_to_async(self.get_object)()


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

    @async_to_sync
    async def list(self, request, *args, **kwargs):
        # For now, we don't have a view:project type permission - we can always view
        # TODO: check permissions for project viewing instead
        authz_middleware.mark_authz_done(request)
        return super().list(request, *args, **kwargs)

    @async_to_sync
    async def create(self, request, *args, **kwargs):
        if not (await authz_middleware.async_evaluate_one(request, RESOURCE_EVERYTHING, P_CREATE_PROJECT)):
            return forbidden(request)

        authz_middleware.mark_authz_done(request)
        return super().create(request, *args, **kwargs)

    @async_to_sync
    async def update(self, request, *args, **kwargs):
        try:
            project = await self.get_obj_async()
        except Http404:
            return not_found(request)

        if not (
            await authz_middleware.async_evaluate_one(
                request, build_resource(project=project.identifier), P_EDIT_PROJECT)
        ):
            return forbidden(request)

        authz_middleware.mark_authz_done(request)
        return super().update(request, *args, **kwargs)

    @async_to_sync
    async def destroy(self, request, *args, **kwargs):
        try:
            project = await self.get_obj_async()
        except Http404:
            return not_found(request)

        can_delete = await authz_middleware.async_evaluate_one(
            request, build_resource(project=project.identifier), P_DELETE_PROJECT)
        if not can_delete:
            return forbidden(request)

        authz_middleware.mark_authz_done(request)
        return super().destroy(request, *args, **kwargs)


class DatasetViewSet(CHORDPublicModelViewSet):
    """
    get:
    Return a list of all existing datasets

    post:
    Create a new dataset
    """

    # TODO: check permissions for dataset viewing instead

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
