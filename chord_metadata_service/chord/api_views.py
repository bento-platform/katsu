import asyncio
import json

from asgiref.sync import async_to_sync, sync_to_async
from bento_lib.auth.permissions import (
    P_CREATE_PROJECT,
    P_EDIT_PROJECT,
    P_DELETE_PROJECT,
    P_CREATE_DATASET,
    P_EDIT_DATASET,
    P_DELETE_DATASET,
    P_DELETE_DATA,
)
from bento_lib.auth.resources import RESOURCE_EVERYTHING, build_resource
from bento_lib.responses import errors

from django.db.models import Prefetch
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet

from chord_metadata_service.authz.middleware import authz_middleware as authz
from chord_metadata_service.authz.permissions import BentoAllowAny, BentoAllowAnyReadOnly, BentoDeferToHandler
from chord_metadata_service.cleanup.run_all import run_all_cleanup
from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope
from chord_metadata_service.discovery.utils import get_discovery_data_type_permissions
from chord_metadata_service.logger import logger
from chord_metadata_service.resources.serializers import ResourceSerializer
from chord_metadata_service.restapi.api_renderers import PhenopacketsRenderer, JSONLDDatasetRenderer, RDFDatasetRenderer
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination
from chord_metadata_service.restapi.utils import response_optionally_as_attachment

from . import data_types as dt
from .models import Project, Dataset, ProjectJsonSchema, DatasetV2, DatasetV2ScopeAdapter, DatasetV2Translation
from .views_data_types import make_data_type_response_object, QUERYSET_FN
from .serializers import (
    ProjectJsonSchemaSerializer,
    ProjectSerializer,
    DatasetSerializer,
    DatasetV2Serializer,
    DatasetV2TranslationSerializer,
)


__all__ = ["ProjectViewSet", "DatasetViewSet"]


def _get_preferred_language(request: DrfRequest) -> str:
    """Normalize the primary language tag from the Accept-Language header."""
    header = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
    if not header:
        return "en"
    primary = header.split(",")[0].split(";")[0].strip()
    return primary.split("-")[0].lower() or "en"


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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["language"] = _get_preferred_language(self.request)
        return context

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        response["Content-Language"] = _get_preferred_language(request)
        return response

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response["Content-Language"] = _get_preferred_language(request)
        return response

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


class DatasetV2ViewSet(CHORDPublicModelViewSet):
    queryset = DatasetV2.objects.all()
    serializer_class = DatasetV2Serializer
    lookup_field = "identifier"

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        language = _get_preferred_language(self.request)
        if language != "en":
            queryset = queryset.prefetch_related(
                Prefetch(
                    "translations",
                    queryset=DatasetV2Translation.objects.filter(language=language),
                    to_attr="prefetched_translations",
                )
            )
        return queryset

    async def get_obj_async(self):
        try:
            return await DatasetV2.objects.aget(identifier=self.kwargs["identifier"])
        except DatasetV2.DoesNotExist:
            raise Http404

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["language"] = _get_preferred_language(self.request)
        return context

    def list(self, request, *args, **kwargs):
        authz.mark_authz_done(request)
        response = super().list(request, *args, **kwargs)
        response["Content-Language"] = _get_preferred_language(request)
        return response

    def retrieve(self, request, *args, **kwargs):
        authz.mark_authz_done(request)
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data  # triggers to_representation, sets _content_language in context
        response = Response(data)
        response["Content-Language"] = serializer.context.get("_content_language", "en")
        return response

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
        dataset_project_id = str(dataset.project_id)

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
                build_resource(project=str(dataset.project_id)),
                P_DELETE_DATASET,
            )
        ):
            return forbidden(request)

        authz.mark_authz_done(request)
        return await sync_to_async(super().destroy)(request, *args, **kwargs)

    @action(detail=True, methods=["get"], url_path="summary", url_name="summary",
            permission_classes=[BentoAllowAny])
    @async_to_sync
    async def summary(self, request):
        identifier = self.kwargs["identifier"]
        dataset = await DatasetV2.objects.filter(identifier=identifier).afirst()
        if dataset is None:
            authz.mark_authz_done(request)
            return Response(errors.not_found_error("Dataset not found"), status=status.HTTP_404_NOT_FOUND)
        authz.mark_authz_done(request)
        return Response({"counts": dataset.data.get("counts") or []})

    @action(detail=True, methods=["get"], url_path="data-types", url_name="data-types",
            permission_classes=[BentoAllowAny])
    @async_to_sync
    async def data_types(self, request):
        identifier = self.kwargs["identifier"]
        try:
            dataset = await DatasetV2.objects.aget(identifier=identifier)
        except DatasetV2.DoesNotExist:
            return Response(errors.not_found_error(f"Dataset {identifier} not found"), status=status.HTTP_404_NOT_FOUND)
        project = await Project.objects.aget(identifier=dataset.project_id)
        discovery_scope = ValidatedDiscoveryScope(project, DatasetV2ScopeAdapter(dataset))
        dt_permissions = await get_discovery_data_type_permissions(request, discovery_scope)
        dt_response = sorted(
            await asyncio.gather(*(
                make_data_type_response_object(dt_id, dt_d, discovery_scope, dt_permissions[dt_id])
                for dt_id, dt_d in dt.DATA_TYPES.items()
            )),
            key=lambda d: d["id"],
        )
        return Response(dt_response)

    @action(detail=True, methods=["get", "delete"],
            url_path=r"data-types/(?P<data_type>[^/.]+)", url_name="data-type",
            permission_classes=[BentoDeferToHandler])
    @async_to_sync
    async def data_type_detail(self, request, data_type):
        identifier = self.kwargs["identifier"]
        try:
            dataset = await DatasetV2.objects.aget(identifier=identifier)
        except DatasetV2.DoesNotExist:
            authz.mark_authz_done(request)
            return Response(errors.not_found_error(f"Dataset {identifier} not found"), status=status.HTTP_404_NOT_FOUND)
        project = await Project.objects.aget(identifier=dataset.project_id)
        project_id = str(project.identifier)

        if data_type not in QUERYSET_FN:
            authz.mark_authz_done(request)
            return Response(errors.not_found_error(f"Data type {data_type} doesn't exist"),
                            status=status.HTTP_404_NOT_FOUND)

        qs = QUERYSET_FN[data_type](identifier)

        if request.method == "DELETE":
            if not (
                await authz.async_evaluate_one(
                    request, build_resource(project_id, identifier, data_type), P_DELETE_DATA
                )
            ):
                authz.mark_authz_done(request)
                return Response(errors.forbidden_error(), status=status.HTTP_403_FORBIDDEN)
            authz.mark_authz_done(request)
            await qs.adelete()
            lg = logger.bind(dataset_id=identifier, data_type=data_type)
            n_removed = await run_all_cleanup(lg)
            await lg.ainfo("ran cleanup after clearing data type via API", n_removed=n_removed)
            return Response(status=status.HTTP_204_NO_CONTENT)

        discovery_scope = ValidatedDiscoveryScope(project, DatasetV2ScopeAdapter(dataset))
        dt_permissions = await get_discovery_data_type_permissions(request, discovery_scope)
        response_object = await make_data_type_response_object(
            data_type, dt.DATA_TYPES[data_type], discovery_scope, permissions=dt_permissions[data_type],
        )
        authz.mark_authz_done(request)
        return Response(response_object)

    @action(detail=True, methods=["get", "post"], url_path="translations", url_name="translations")
    @async_to_sync
    async def translations(self, request):
        identifier = self.kwargs["identifier"]
        if request.method == "GET":
            authz.mark_authz_done(request)
            serializer = DatasetV2TranslationSerializer(
                [t async for t in DatasetV2Translation.objects.filter(dataset_id=identifier)],
                many=True,
                context=self.get_serializer_context(),
            )
            return Response(serializer.data)

        try:
            dataset = await DatasetV2.objects.aget(identifier=identifier)
        except DatasetV2.DoesNotExist:
            return not_found(request)

        if not (
            await authz.async_evaluate_one(
                request,
                build_resource(project=str(dataset.project_id), dataset=str(dataset.identifier)),
                P_EDIT_DATASET,
            )
        ):
            return forbidden(request)

        authz.mark_authz_done(request)
        serializer = DatasetV2TranslationSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        instance = DatasetV2Translation.from_schema(
            serializer._validated_schema, dataset_id=str(dataset.identifier)
        )
        await instance.asave()
        return Response(serializer.to_representation(instance), status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "put", "delete"],
            url_path=r"translations/(?P<language>[^/.]+)", url_name="translation")
    @async_to_sync
    async def translation_detail(self, request, language):
        identifier = self.kwargs["identifier"]
        try:
            translation = await DatasetV2Translation.objects.aget(dataset_id=identifier, language=language)
        except DatasetV2Translation.DoesNotExist:
            return not_found(request)

        if request.method == "GET":
            authz.mark_authz_done(request)
            serializer = DatasetV2TranslationSerializer(translation, context=self.get_serializer_context())
            return Response(serializer.data)

        dataset = await DatasetV2.objects.aget(identifier=identifier)

        if not (
            await authz.async_evaluate_one(
                request,
                build_resource(project=str(dataset.project_id), dataset=str(dataset.identifier)),
                P_EDIT_DATASET,
            )
        ):
            return forbidden(request)

        if request.method == "DELETE":
            await translation.adelete()
            authz.mark_authz_done(request)
            return Response(status=status.HTTP_204_NO_CONTENT)

        # PUT
        authz.mark_authz_done(request)
        serializer = DatasetV2TranslationSerializer(
            translation, data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        await sync_to_async(serializer.save)()
        return Response(serializer.data)


class DatasetV2TranslationViewSet(CHORDPublicModelViewSet):
    serializer_class = DatasetV2TranslationSerializer
    lookup_field = "language"

    def get_queryset(self):
        return DatasetV2Translation.objects.filter(dataset_id=self.kwargs["identifier"])

    async def get_dataset_async(self) -> DatasetV2:
        try:
            return await DatasetV2.objects.aget(identifier=self.kwargs["identifier"])
        except DatasetV2.DoesNotExist:
            raise Http404

    async def get_obj_async(self):
        try:
            return await DatasetV2Translation.objects.aget(
                dataset_id=self.kwargs["identifier"],
                language=self.kwargs["language"],
            )
        except DatasetV2Translation.DoesNotExist:
            raise Http404

    def list(self, request, *args, **kwargs):
        authz.mark_authz_done(request)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        authz.mark_authz_done(request)
        return super().retrieve(request, *args, **kwargs)

    @async_to_sync
    async def create(self, request, *args, **kwargs):
        try:
            dataset = await self.get_dataset_async()
        except Http404:
            return not_found(request)

        if not (
            await authz.async_evaluate_one(
                request,
                build_resource(project=str(dataset.project_id), dataset=str(dataset.identifier)),
                P_EDIT_DATASET,
            )
        ):
            return forbidden(request)

        authz.mark_authz_done(request)

        # PydanticJSONBSerializer.create() ignores validated_data, so call from_schema directly
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = DatasetV2Translation.from_schema(
            serializer._validated_schema, dataset_id=str(dataset.identifier)
        )
        await instance.asave()
        return Response(serializer.to_representation(instance), status=status.HTTP_201_CREATED)

    @async_to_sync
    async def update(self, request, *args, **kwargs):
        try:
            await self.get_obj_async()
        except Http404:
            return not_found(request)

        dataset = await self.get_dataset_async()

        if not (
            await authz.async_evaluate_one(
                request,
                build_resource(project=str(dataset.project_id), dataset=str(dataset.identifier)),
                P_EDIT_DATASET,
            )
        ):
            return forbidden(request)

        authz.mark_authz_done(request)
        return await sync_to_async(super().update)(request, *args, **kwargs)

    @async_to_sync
    async def destroy(self, request, *args, **kwargs):
        try:
            translation = await self.get_obj_async()
        except Http404:
            return not_found(request)

        dataset = await self.get_dataset_async()

        if not (
            await authz.async_evaluate_one(
                request,
                build_resource(project=str(dataset.project_id), dataset=str(dataset.identifier)),
                P_EDIT_DATASET,
            )
        ):
            return forbidden(request)

        await translation.adelete()
        authz.mark_authz_done(request)
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
