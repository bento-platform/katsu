from asgiref.sync import async_to_sync
from bento_lib.auth.permissions import P_QUERY_DATA, Permission, P_INGEST_DATA, P_DELETE_DATA
from django.conf import settings
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request as DrfRequest

from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.discovery.scope import get_request_discovery_scope, INSTANCE_SCOPE, ValidatedDiscoveryScope
from chord_metadata_service.discovery.scopeable_model import BaseScopeableModel

from .middleware import authz_middleware


__all__ = [
    "BentoAllowAny",
    "BentoAllowAnyReadOnly",
    "BentoDeferToHandler",
    "BentoPhenopacketDataPermission",
    "BentoExperimentDataPermission",
    "ReadOnly",
    "OverrideOrSuperUserOnly",
]


# TODO: new base permissions for authz


class BentoAllowAny(BasePermission):
    def has_permission(self, request, view):
        # Mutate the request object using the middlware call
        authz_middleware.mark_authz_done(request)
        return True


class BentoAllowAnyReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            # Mutate the request object using the middlware call
            authz_middleware.mark_authz_done(request)
            return True
        return False  # Can be made True later by downstream permissions checks


class BentoDeferToHandler(BasePermission):
    def has_permission(self, _request, _view):
        return True  # we return true, like AllowAny, but we don't mark authz as done - so we defer it to the handler


async def _get_scope_for_request_and_api_view(request: DrfRequest, view) -> ValidatedDiscoveryScope:
    if getattr(view, "scope_enabled", False):
        return await get_request_discovery_scope(request)
    else:
        return INSTANCE_SCOPE


async def view_request_has_data_type_permission(
    request: DrfRequest, view, data_type: str, scope: ValidatedDiscoveryScope | None = None
) -> bool:
    # We MUST specifically mark view sets as scope-enabled (which means their queryset handles scope correctly);
    # otherwise, we cannot scope into a specific project/dataset and must use the whole instance as the scope.
    # Otherwise, we can could leak data from other projects/datasets.
    # TODO: there must be a better way to enforce this without manual flagging

    _scope: ValidatedDiscoveryScope = scope or await _get_scope_for_request_and_api_view(request, view)

    p: Permission

    if request.method == "GET":
        p = P_QUERY_DATA
    elif request.method in ("POST", "PUT"):
        p = P_INGEST_DATA
    elif request.method == "DELETE":
        p = P_DELETE_DATA
    else:
        return False

    return await authz_middleware.async_evaluate_one(
        request, _scope.as_authz_resource(data_type=data_type), p, mark_authz_done=True
    )


async def _has_data_type_permission_obj(request: DrfRequest, view, data_type: str, obj: BaseScopeableModel) -> bool:
    scope = await _get_scope_for_request_and_api_view(request, view)

    if not await obj.scope_contains_object_async(scope):
        return False

    return await view_request_has_data_type_permission(request, view, data_type, scope)


class BentoPhenopacketDataPermission(BasePermission):
    @async_to_sync
    async def has_permission(self, request: DrfRequest, view):
        return await view_request_has_data_type_permission(request, view, DATA_TYPE_PHENOPACKET)

    @async_to_sync
    async def has_object_permission(self, request, view, obj: BaseScopeableModel):
        return await _has_data_type_permission_obj(request, view, DATA_TYPE_PHENOPACKET, obj)


class BentoExperimentDataPermission(BasePermission):
    @async_to_sync
    async def has_permission(self, request: DrfRequest, view):
        return await view_request_has_data_type_permission(request, view, DATA_TYPE_EXPERIMENT)

    @async_to_sync
    async def has_object_permission(self, request, view, obj: BaseScopeableModel):
        return await _has_data_type_permission_obj(request, view, DATA_TYPE_PHENOPACKET, obj)


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class OverrideOrSuperUserOnly(BasePermission):
    def has_permission(self, request, view):
        # If in CHORD production, is_superuser will be set by remote user headers.
        # TODO: Configuration: Allow configurable read-only APIs or other external access
        return settings.AUTH_OVERRIDE or request.user.is_superuser
