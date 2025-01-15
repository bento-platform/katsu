from rest_framework.views import exception_handler

from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.discovery.exceptions import DiscoveryScopeException

__all__ = ["katsu_exception_handler"]


def katsu_exception_handler(exc, context):
    # Start with default DRF exception handler
    response = exception_handler(exc, context)

    if isinstance(exc, DiscoveryScopeException):
        # Allow scope exception responses through the authz middleware (mark them as authorized)
        authz_middleware.mark_authz_done(context["request"])

    return response
