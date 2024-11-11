from asgiref.sync import async_to_sync
from django.conf import settings
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request as DrfRequest

from chord_metadata_service.discovery.scopeable_model import BaseScopeableModel

from .middleware import authz_middleware


__all__ = [
    "BentoAllowAny",
    "BentoAllowAnyReadOnly",
    "BentoDeferToHandler",
    "BentoDataTypePermission",
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


class BentoDataTypePermission(BasePermission):
    @async_to_sync
    async def has_permission(self, request: DrfRequest, view):
        # view: BentoAuthzModelViewSet (cannot annotate due to circular import)
        if view.data_type is None:
            raise NotImplemented("BentoAuthzModelViewSet DATA_TYPE must be set")
        return await view.request_has_data_type_permissions(request)

    @async_to_sync
    async def has_object_permission(self, request: DrfRequest, view, obj: BaseScopeableModel):
        # view: BentoAuthzModelViewSet (cannot annotate due to circular import)
        # if this is called, has_data_type_permission has already been called and handled the overall action type
        # TODO: eliminate duplicate scope check somehow without enabling permissions on objects outside of scope
        return await view.obj_is_in_request_scope(request, obj)


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class OverrideOrSuperUserOnly(BasePermission):
    def has_permission(self, request, view):
        # If in CHORD production, is_superuser will be set by remote user headers.
        # TODO: Configuration: Allow configurable read-only APIs or other external access
        return settings.AUTH_OVERRIDE or request.user.is_superuser
