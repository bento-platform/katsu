from django.conf import settings
from rest_framework.permissions import BasePermission, SAFE_METHODS
from .middleware import authz_middleware


__all__ = [
    "BentoAllowAny",
    "BentoAllowAnyReadOnly",
    "BentoDeferToHandler",
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


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class OverrideOrSuperUserOnly(BasePermission):
    def has_permission(self, request, view):
        # If in CHORD production, is_superuser will be set by remote user headers.
        # TODO: Configuration: Allow configurable read-only APIs or other external access
        return settings.AUTH_OVERRIDE or request.user.is_superuser
