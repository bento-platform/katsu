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
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet

from chord_metadata_service.authz.middleware import authz_middleware as authz
from chord_metadata_service.authz.permissions import BentoAllowAnyReadOnly, BentoDeferToHandler
from chord_metadata_service.cleanup.run_all import run_all_cleanup
from chord_metadata_service.logger import logger
from chord_metadata_service.resources.serializers import ResourceSerializer
from chord_metadata_service.restapi.api_renderers import PhenopacketsRenderer, JSONLDDatasetRenderer, RDFDatasetRenderer
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination
from chord_metadata_service.restapi.utils import response_optionally_as_attachment

from .models import Project, Dataset, ProjectJsonSchema, DatasetV2
from .serializers import (
    ProjectJsonSchemaSerializer,
    ProjectSerializer,
    DatasetSerializer,
    DatasetV2Serializer,
)


__all__ = ["ProjectViewSet", "DatasetViewSet"]


def bad_request(request: DrfRequest, *args):
    authz.mark_authz_done(request)
    return Response(errors.bad_request_error(*args), status=status.HTTP_400_BAD_REQUEST)


def forbidden(request: DrfRequest):
    authz.mark_authz_done(request)
    return Response(errors.forbidden_error(), status=status.HTTP_403_FORBIDDEN)


def not_found(request: DrfRequest):
    authz.mark_authz_done(request)
    return Response(errors.not_found_error(), status=status.HTTP_404_NOT_FOUND)


class CHORDPublicModelViewSet(ModelViewSet):
    permission_classes = [BentoAllowAnyReadOnly | BentoDeferToHandler]
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (PhenopacketsRenderer,)
    pagination_class = LargeResultsSetPagination

    async def get_obj_async(self):
        return await sync_to_async(self.get_object)()


class ProjectViewSet(CHORDPublicModelViewSet):
    """
    get:
    Return a list of all existing projects

    post:
    Create a new project
    """

    queryset = Project.objects.prefetch_related("dv2").order_by("identifier")
    serializer_class = ProjectSerializer

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
    lookup_url_kwarg = "dataset_id"

    serializer_class = DatasetSerializer
    renderer_classes = tuple(CHORDPublicModelViewSet.renderer_classes) + (JSONLDDatasetRenderer, RDFDatasetRenderer,)
    queryset = Dataset.objects.all().order_by("title")

    @action(detail=True, methods=['get'])
    def dats(self, request: DrfRequest, *_args, **_kwargs):
        """
        Retrieve a specific DATS file for a given dataset.

        Return the DATS file as a JSON response or an error if not found.
        """
        try:
            dataset = self.get_object()
        except Http404:
            return not_found(request)  # side effect: sets authz done flag

        authz.mark_authz_done(request)

        return response_optionally_as_attachment(request, dataset.dats_file, f"{dataset.identifier}_dats.json")

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

        dataset_id = str(dataset.identifier)

        if not (
            await authz.async_evaluate_one(request, build_resource(project=str(dataset.project_id)), P_DELETE_DATASET)
        ):
            return forbidden(request)  # side effect: sets authz done flag

        await dataset.adelete()

        lg = logger.bind(dataset_id=dataset_id)
        n_removed = await run_all_cleanup(lg)
        await lg.ainfo("ran cleanup after deleting dataset via DRF API", n_removed=n_removed)

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
            return bad_request(request, "No project ID in request body")  # side effect: sets authz done flag

        if not (await authz.async_evaluate_one(request, build_resource(project=project_id), P_CREATE_DATASET)):
            return forbidden(request)  # side effect: sets authz done flag

        authz.mark_authz_done(request)

        if error_msg := self._parse_dats(request):
            return bad_request(request, error_msg)

        return await sync_to_async(super().create)(request, *args, **kwargs)

    @async_to_sync
    async def update(self, request, *args, **kwargs):
        try:
            dataset = await self.get_obj_async()
        except Http404:
            return not_found(request)  # side effect: sets authz done flag

        dataset_project_id = str(dataset.project_id)

        if not (
            await authz.async_evaluate_one(
                request,
                build_resource(project=dataset_project_id, dataset=str(dataset.identifier)),
                P_EDIT_DATASET,
            )
        ):
            return forbidden(request)  # side effect: sets authz done flag

        # Do not allow datasets to change project
        if "project" in request.data and request.data["project"] != dataset_project_id:
            return bad_request(request, "Dataset project ID cannot change")

        authz.mark_authz_done(request)

        if error_msg := self._parse_dats(request):
            return bad_request(request, error_msg)

        return await sync_to_async(super().update)(request, *args, **kwargs)  # TODO: handle invalid


# class DatasetV2ViewSet(CHORDPublicModelViewSet):
#     queryset = DatasetV2.objects.all()
#     serializer_class = DatasetV2Serializer
#     lookup_field = 'id'

#     def get_queryset(self):
#         queryset = super().get_queryset()
#
#         project_id = self.request.query_params.get('project_id')
#         if project_id:
#             queryset = queryset.filter(project_id=project_id)
#
#         return queryset

#     def perform_create(self, serializer):
#         instance = serializer.save()
#         instance.save()

#     def perform_update(self, serializer):
#         instance = serializer.save()
#         instance.save()

class DatasetV2ViewSet(CHORDPublicModelViewSet):
    queryset = DatasetV2.objects.all()
    serializer_class = DatasetV2Serializer
    lookup_field = "identifier"
    DEFAULT_LANGUAGE = "en"

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        lang = self.request.query_params.get("lang")
        if lang:
            queryset = queryset.filter(language=lang)
        return queryset

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        language = self.request.query_params.get("lang", self.DEFAULT_LANGUAGE)
        obj = get_object_or_404(
            queryset,
            identifier=self.kwargs["identifier"],
            language=language,
        )
        self.check_object_permissions(self.request, obj)
        return obj

    async def get_obj_async(self):
        language = self.request.query_params.get("lang", self.DEFAULT_LANGUAGE)  # type: ignore
        try:
            return await DatasetV2.objects.aget(
                identifier=self.kwargs["identifier"],
                language=language,
            )
        except DatasetV2.DoesNotExist:
            raise Http404

    def list(self, request, *args, **kwargs):
        authz.mark_authz_done(request)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        authz.mark_authz_done(request)
        return super().retrieve(request, *args, **kwargs)

    @async_to_sync
    async def create(self, request, *args, **kwargs):
        project_id = request.data.get("project")

        if project_id is None:
            return bad_request(request, "No project ID in request body")
        if not (
            await authz.async_evaluate_one(
                request,
                build_resource(project=str(project_id)),
                P_CREATE_DATASET,
            )
        ):
            return forbidden(request)

        authz.mark_authz_done(request)
        return await sync_to_async(super().create)(request, *args, **kwargs)

    @async_to_sync
    async def update(self, request, *args, **kwargs):
        try:
            dataset = await self.get_obj_async()
        except Http404:
            return not_found(request)
        dataset_project_id = str(dataset.project)

        if not (
            await authz.async_evaluate_one(
                request,
                build_resource(
                    project=dataset_project_id,
                    dataset=str(dataset.identifier),
                ),
                P_EDIT_DATASET,
            )
        ):
            return forbidden(request)

        incoming_project = request.data.get("project") or request.data.get("project_id")
        if incoming_project is not None and str(incoming_project) != dataset_project_id:
            return bad_request(request, "Dataset project ID cannot change")

        authz.mark_authz_done(request)
        return await sync_to_async(super().update)(request, *args, **kwargs)

    @async_to_sync
    async def destroy(self, request, *args, **kwargs):
        try:
            dataset = await self.get_obj_async()
        except Http404:
            return not_found(request)

        if not (
            await authz.async_evaluate_one(
                request,
                build_resource(project=str(dataset.project)),
                P_DELETE_DATASET,
            )
        ):
            return forbidden(request)

        authz.mark_authz_done(request)
        return await sync_to_async(super().destroy)(request, *args, **kwargs)


class ProjectJsonSchemaViewSet(CHORDPublicModelViewSet):
    """
    get:
    Return list of ProjectJsonSchema

    post:
    Create a new ProjectJsonSchema
    """

    queryset = ProjectJsonSchema.objects.all().order_by("project_id")
    serializer_class = ProjectJsonSchemaSerializer

    @async_to_sync
    async def create(self, request, *args, **kwargs):
        project_id = request.data.get("project")

        if project_id is None:
            return bad_request(request, "No project ID in request body")  # side effect: sets authz done flag

        if not (await authz.async_evaluate_one(request, build_resource(project=project_id), P_EDIT_PROJECT)):
            return forbidden(request)  # side effect: sets authz done flag

        authz.mark_authz_done(request)
        return await sync_to_async(super().create)(request, *args, **kwargs)

    @async_to_sync
    async def update(self, request, *args, **kwargs):
        try:
            pjs = await self.get_obj_async()
        except Http404:
            return not_found(request)  # side effect: sets authz done flag

        if not (await authz.async_evaluate_one(request, build_resource(project=str(pjs.project_id)), P_EDIT_PROJECT)):
            return forbidden(request)  # side effect: sets authz done flag

        authz.mark_authz_done(request)
        return await sync_to_async(super().update)(request, *args, **kwargs)

    @async_to_sync
    async def destroy(self, request, *args, **kwargs):
        try:
            pjs = await self.get_obj_async()
        except Http404:
            return not_found(request)  # side effect: sets authz done flag

        if not (await authz.async_evaluate_one(request, build_resource(project=str(pjs.project_id)), P_EDIT_PROJECT)):
            return forbidden(request)  # side effect: sets authz done flag

        authz.mark_authz_done(request)
        return await sync_to_async(super().destroy)(request, *args, **kwargs)
