from bento_lib.responses import errors
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from structlog.stdlib import BoundLogger
# TODO: py3.11:
#  from typing import LiteralString

from chord_metadata_service.authz.middleware import authz_middleware

__all__ = [
    "INSUFFICIENT_DATA_AVAILABLE",
    "INSUFFICIENT_PRIVILEGES",
    "insufficient_privileges",
    "NO_PUBLIC_DATA_AVAILABLE",
    "no_public_data",
    "NO_PUBLIC_FIELDS_CONFIGURED",
]

# Public response when there is no enough data that passes the project-custom threshold
INSUFFICIENT_DATA_AVAILABLE = {"message": "Insufficient data available."}

# Public response when there is insufficient permissions to view the overview
INSUFFICIENT_PRIVILEGES = {"message": "Insufficient privileges to view data."}


def insufficient_privileges(request: Request):
    authz_middleware.mark_authz_done(request)  # may have already been done if endpoint has BentoAllowAny permissions
    return Response(INSUFFICIENT_PRIVILEGES, status=status.HTTP_403_FORBIDDEN)


# Public response when there is no public data available and config file is not provided
NO_PUBLIC_DATA_AVAILABLE = {"message": "No public data available."}


def no_public_data(request: Request):
    authz_middleware.mark_authz_done(request)  # may have already been done if endpoint has BentoAllowAny permissions
    return Response(NO_PUBLIC_DATA_AVAILABLE, status=status.HTTP_404_NOT_FOUND)


# Public response when public fields are not configured and config file is not provided
NO_PUBLIC_FIELDS_CONFIGURED = {"message": "No public fields configured."}


async def django_validation_error(
    request: Request, e: ValidationError, logger: BoundLogger, logger_event: str  # TODO: py3.11: LiteralString
):
    await logger.ainfo(logger_event, exc=e)
    authz_middleware.mark_authz_done(request)
    return Response(errors.bad_request_error(
        *(e.error_list if hasattr(e, "error_list") else e.error_dict.items()),
    ), status=status.HTTP_400_BAD_REQUEST)
