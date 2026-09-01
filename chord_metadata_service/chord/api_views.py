import asyncio

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

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Prefetch
from django.http import Http404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet

from chord_metadata_service.authz.helpers import get_data_type_query_permissions
from chord_metadata_service.authz.middleware import authz_middleware as authz
from chord_metadata_service.authz.permissions import BentoAllowAny, BentoAllowAnyReadOnly, BentoDeferToHandler
from chord_metadata_service.cleanup.run_all import run_all_cleanup
from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope
from chord_metadata_service.experiments.summaries import dt_experiment_summary
from chord_metadata_service.phenopackets.summaries import dt_phenopacket_summary
from chord_metadata_service.logger import logger
from chord_metadata_service.resources.serializers import ResourceSerializer
from chord_metadata_service.restapi.api_renderers import PhenopacketsRenderer
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination

from .data_types import DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from .models import Project, ProjectJsonSchema, Dataset, DatasetTranslation
from .serializers import (
    ProjectJsonSchemaSerializer,
    ProjectSerializer,
    DatasetSerializer,
    DatasetTranslationSerializer,
)


__all__ = ["ProjectViewSet", "DatasetViewSet"]


def _serializer_error_messages(errs: dict) -> list[str]:
    msgs = []
    for field, field_errors in errs.items():
        prefix = "" if field == api_settings.NON_FIELD_ERRORS_KEY else f"{field}: "
        if isinstance(field_errors, list):
            msgs.extend(f"{prefix}{e}" for e in field_errors)
        else:
            msgs.append(f"{prefix}{field_errors}")
    return msgs


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

    queryset = Project.objects.prefetch_related("datasets").order_by("identifier")
    serializer_class = ProjectSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["language"] = _get_preferred_language(self.request)
        return context

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
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    lookup_field = "identifier"

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        queryset = queryset.prefetch_related("translations")
        language = _get_preferred_language(self.request)
        if language != "en":
            queryset = queryset.prefetch_related(
                Prefetch(
                    "translations",
                    queryset=DatasetTranslation.objects.filter(language=language),
                    to_attr="prefetched_translations",
                )
            )
        return queryset

    async def get_obj_async(self):
        try:
            return await Dataset.objects.aget(identifier=self.kwargs["identifier"])
        except Dataset.DoesNotExist:
            raise Http404

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["language"] = _get_preferred_language(self.request)
        return context

    def list(self, request, *args, **kwargs):
        authz.mark_authz_done(request)
        return super().list(request, *args, **kwargs)

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

        def _do():
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    errors.bad_request_error(*_serializer_error_messages(serializer.errors)),
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=self.get_success_headers(serializer.data)
            )

        return await sync_to_async(_do)()

    @async_to_sync
    async def update(self, request, **kwargs):
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

        partial = kwargs.get("partial", False)

        def _do():
            serializer = self.get_serializer(dataset, data=request.data, partial=partial)
            if not serializer.is_valid():
                return Response(
                    errors.bad_request_error(*_serializer_error_messages(serializer.errors)),
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save()
            return Response(serializer.data)

        return await sync_to_async(_do)()

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

        dataset_id = str(dataset.identifier)
        await dataset.adelete()

        lg = logger.bind(dataset_id=dataset_id)
        n_removed = await run_all_cleanup(lg)
        await lg.ainfo("ran cleanup after deleting dataset via DRF API", n_removed=n_removed)

        authz.mark_authz_done(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path="resources", url_name="resources")
    def resources(self, request, *_args, **_kwargs):
        try:
            dataset = self.get_object()
        except Http404:
            return not_found(request)
        authz.mark_authz_done(request)
        return Response(ResourceSerializer(dataset.resources, many=True).data)

    @async_to_sync
    @action(detail=True, methods=["get"], url_path="summary", url_name="summary", permission_classes=[BentoAllowAny])
    async def summary(self, request, **kwargs):
        identifier = self.kwargs["identifier"]
        try:
            dataset = await Dataset.objects.aget(identifier=identifier)
        except (Dataset.DoesNotExist, DjangoValidationError):
            return Response(errors.not_found_error("Dataset not found"), status=status.HTTP_404_NOT_FOUND)

        project = await Project.objects.aget(identifier=dataset.project_id)
        discovery_scope = ValidatedDiscoveryScope(project, dataset)

        summary_functions = {
            DATA_TYPE_PHENOPACKET: dt_phenopacket_summary,
            DATA_TYPE_EXPERIMENT: dt_experiment_summary,
        }

        dt_permissions = await get_data_type_query_permissions(
            request,
            data_types=list(summary_functions.keys()),
            resource=discovery_scope.as_authz_resource(),
        )

        summaries = await asyncio.gather(
            *[
                summary_functions[data_type](discovery_scope, dt_permissions[data_type])
                for data_type in summary_functions
            ]
        )

        return Response(dict(zip(summary_functions.keys(), summaries)))

    @async_to_sync
    @action(
        detail=True,
        methods=["get", "post"],
        url_path="translations",
        url_name="translations-list",
        permission_classes=[BentoAllowAnyReadOnly | BentoDeferToHandler],
    )
    async def translations(self, request, **kwargs):
        identifier = self.kwargs["identifier"]
        if request.method == "GET":
            authz.mark_authz_done(request)
            qs = DatasetTranslation.objects.filter(dataset_id=identifier)

            def _list():
                items = list(qs)
                page = self.paginate_queryset(items)
                return self.get_paginated_response(DatasetTranslationSerializer(page, many=True).data)

            return await sync_to_async(_list)()
        try:
            dataset = await Dataset.objects.aget(identifier=identifier)
        except Dataset.DoesNotExist:
            return not_found(request)
        if not (
            await authz.async_evaluate_one(
                request, build_resource(project=str(dataset.project_id), dataset=identifier), P_EDIT_DATASET
            )
        ):
            return forbidden(request)
        authz.mark_authz_done(request)
        serializer = DatasetTranslationSerializer(data=request.data, context=self.get_serializer_context())

        def _create():
            serializer.is_valid(raise_exception=True)
            instance = DatasetTranslation.from_schema(serializer._validated_schema, dataset_id=identifier)
            instance.save()
            return Response(serializer.to_representation(instance), status=status.HTTP_201_CREATED)

        return await sync_to_async(_create)()

    @async_to_sync
    @action(
        detail=True,
        methods=["get", "put", "delete"],
        url_path=r"translations/(?P<language>[^/.]+)",
        url_name="translations-detail",
        permission_classes=[BentoAllowAnyReadOnly | BentoDeferToHandler],
    )
    async def translation_detail(self, request, language, **kwargs):
        identifier = self.kwargs["identifier"]
        try:
            translation = await DatasetTranslation.objects.aget(dataset_id=identifier, language=language)
        except DatasetTranslation.DoesNotExist:
            return not_found(request)
        if request.method == "GET":
            authz.mark_authz_done(request)
            return Response(DatasetTranslationSerializer(translation).to_representation(translation))
        try:
            dataset = await Dataset.objects.aget(identifier=identifier)
        except Dataset.DoesNotExist:  # pragma: no cover
            return not_found(request)  # pragma: no cover
        if not (
            await authz.async_evaluate_one(
                request, build_resource(project=str(dataset.project_id), dataset=identifier), P_EDIT_DATASET
            )
        ):
            return forbidden(request)
        authz.mark_authz_done(request)
        if request.method == "DELETE":
            await translation.adelete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = DatasetTranslationSerializer(translation, data=request.data, context=self.get_serializer_context())

        def _update():
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.to_representation(serializer.instance))

        return await sync_to_async(_update)()


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
