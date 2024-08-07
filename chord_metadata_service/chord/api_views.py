import json
import logging

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
from rest_framework import status
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from chord_metadata_service.authz.middleware import authz_middleware as authz
from chord_metadata_service.authz.permissions import BentoAllowAnyReadOnly, BentoDeferToHandler
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


def bad_request(request: DrfRequest):
    authz.mark_authz_done(request)
    return Response(errors.bad_request_error(), status=status.HTTP_400_BAD_REQUEST)


def forbidden(request: DrfRequest):
    authz.mark_authz_done(request)
    return Response(errors.forbidden_error(), status=status.HTTP_403_FORBIDDEN)


def not_found(request: DrfRequest):
    authz.mark_authz_done(request)
    return Response(errors.not_found_error(), status=status.HTTP_404_NOT_FOUND)


class CHORDModelViewSet(ModelViewSet):
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (PhenopacketsRenderer,)
    pagination_class = LargeResultsSetPagination
    permission_classes = [OverrideOrSuperUserOnly]  # Explicit

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

    def list(self, request, *args, **kwargs):
        # For now, we don't have a view:project type permission - we can always view
        # TODO: check permissions for project viewing instead
        authz.mark_authz_done(request)
        return super().list(request, *args, **kwargs)

    @async_to_sync
    async def create(self, request, *args, **kwargs):
        if not (await authz.async_evaluate_one(request, RESOURCE_EVERYTHING, P_CREATE_PROJECT)):
            return forbidden(request)

        authz.mark_authz_done(request)
        return await sync_to_async(super().create)(request, *args, **kwargs)

    @async_to_sync
    async def update(self, request, *args, **kwargs):
        try:
            project = await self.get_obj_async()
        except Http404:
            return not_found(request)

        if not (
            await authz.async_evaluate_one(request, build_resource(project=str(project.identifier)), P_EDIT_PROJECT)
        ):
            return forbidden(request)

        authz.mark_authz_done(request)
        return await sync_to_async(super().update)(request, *args, **kwargs)

    @async_to_sync
    async def destroy(self, request, *args, **kwargs):
        try:
            project = await self.get_obj_async()
        except Http404:
            return not_found(request)

        if not (
            await authz.async_evaluate_one(request, build_resource(project=str(project.identifier)), P_DELETE_PROJECT)
        ):
            return forbidden(request)

        authz.mark_authz_done(request)
        return await sync_to_async(super().destroy)(request, *args, **kwargs)


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
    def dats(self, request, *_args, **_kwargs):
        """
        Retrieve a specific DATS file for a given dataset.

        Return the DATS file as a JSON response or an error if not found.
        """
        try:
            dataset = self.get_object()
        except Http404:
            return not_found(request)  # side effect: sets authz done flag

        authz.mark_authz_done(request)
        return Response(dataset.dats_file)

    @action(detail=True, methods=["get"])
    def resources(self, request, *_args, **_kwargs):
        """
        Retrieve all resources (phenopackets/additional_resources) for a dataset and return a JSON response serialized
        using ResourceSerializer
        """
        try:
            dataset = self.get_object()
        except Http404:
            return not_found(request)  # side effect: sets authz done flag

        authz.mark_authz_done(request)
        return Response(ResourceSerializer(dataset.resources.all(), many=True).data)

    def list(self, request, *args, **kwargs):
        # For now, we don't have a view:dataset type permission - we can always view
        authz.mark_authz_done(request)
        return super().list(request, *args, **kwargs)

    @async_to_sync
    async def destroy(self, request, *args, **kwargs):
        try:
            dataset = await self.get_obj_async()
        except Http404:
            return not_found(request)  # side effect: sets authz done flag

        if not (
            await authz.async_evaluate_one(request, build_resource(project=str(dataset.project_id)), P_DELETE_DATASET)
        ):
            return forbidden(request)  # side effect: sets authz done flag

        await dataset.adelete()

        logger.info(f"Running cleanup after deleting dataset {dataset.identifier} via DRF API")
        n_removed = await run_all_cleanup()
        logger.info(f"Cleanup: removed {n_removed} objects in total")

        authz.mark_authz_done(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _parse_dats(request) -> str | None:
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

    @async_to_sync
    async def create(self, request, *args, **kwargs):
        """
        Creates a Dataset.
        If the request's dats_file is a string, it will be parsed to JSON.
        """

        project_id = request.data.get("project")

        if project_id is None:
            return bad_request(request)  # side effect: sets authz done flag

        if not (await authz.async_evaluate_one(request, build_resource(project=project_id), P_CREATE_DATASET)):
            return forbidden(request)  # side effect: sets authz done flag

        authz.mark_authz_done(request)

        if error_msg := self._parse_dats(request):
            return Response(error_msg, status.HTTP_400_BAD_REQUEST)

        return await sync_to_async(super().create)(request, *args, **kwargs)

    @async_to_sync
    async def update(self, request, *args, **kwargs):
        try:
            dataset = await self.get_obj_async()
        except Http404:
            return not_found(request)  # side effect: sets authz done flag

        if not (
            await authz.async_evaluate_one(
                request,
                build_resource(project=str(dataset.project_id), dataset=str(dataset.identifier)),
                P_EDIT_DATASET,
            )
        ):
            return forbidden(request)  # side effect: sets authz done flag

        # Do not allow datasets to change project
        # TODO

        authz.mark_authz_done(request)

        if error_msg := self._parse_dats(request):
            return Response(error_msg, status.HTTP_400_BAD_REQUEST)

        return await sync_to_async(super().update)(request, *args, **kwargs)  # TODO: handle invalid


class ProjectJsonSchemaViewSet(CHORDPublicModelViewSet):
    """
    get:
    Return list of ProjectJsonSchema

    post:
    Create a new ProjectJsonSchema
    """

    queryset = ProjectJsonSchema.objects.all().order_by("project_id")
    serializer_class = ProjectJsonSchemaSerializer
