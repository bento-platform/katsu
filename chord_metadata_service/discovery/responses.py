import json

from bento_lib.responses import errors
from csv import DictWriter
from django.core.exceptions import ValidationError
from io import StringIO
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from structlog.stdlib import BoundLogger
from typing import LiteralString, Sequence

from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.discovery.types import AcceptedDiscoveryResponseFormats

__all__ = [
    "INSUFFICIENT_DATA_AVAILABLE_MSG",
    "INSUFFICIENT_DATA_AVAILABLE",
    "INSUFFICIENT_PRIVILEGES",
    "insufficient_privileges",
    "NO_PUBLIC_DATA_AVAILABLE",
    "no_public_data",
    "NO_PUBLIC_FIELDS_CONFIGURED",
    "no_public_fields",
    "csv_or_json_error_response",
    "django_validation_error",
]

# Public response when there is no enough data that passes the project-custom threshold
INSUFFICIENT_DATA_AVAILABLE_MSG = "Insufficient data available."
INSUFFICIENT_DATA_AVAILABLE = {"message": INSUFFICIENT_DATA_AVAILABLE_MSG}

# Public response when there is insufficient permissions to view the overview
INSUFFICIENT_PRIVILEGES = {"message": "Insufficient privileges to view data."}


def _error_csv_utf8_bytes(field_names: Sequence[str], row_dict: dict) -> bytes:
    res_csv_io = StringIO()
    w = DictWriter(res_csv_io, fieldnames=field_names)
    w.writeheader()
    w.writerow(row_dict)
    res_csv_io.seek(0)
    return res_csv_io.read().encode("utf-8")


def _public_error_response(
    request: Request, status_code: int, response: dict, accepted_formats: AcceptedDiscoveryResponseFormats
) -> Response:
    authz_middleware.mark_authz_done(request)  # may have already been done if endpoint has BentoAllowAny permissions
    if "csv" in accepted_formats and "json" not in accepted_formats:
        # csv error response (for discovery matches endpoint)
        csv_bytes = _error_csv_utf8_bytes(["message"], response)
        return Response(csv_bytes, status=status_code, content_type="text/csv")
    # fall back to JSON
    return Response(response, status=status_code)


def insufficient_privileges(
    request: Request, accepted_formats: AcceptedDiscoveryResponseFormats = frozenset(("json",))
):
    """
    Returns our (non-Bento-standard) Katsu discovery "insufficient privileges" error in either JSON or CSV form.
    This is kept in its current form to maintain backwards compatibility with the previous "public" API's errors.
    """
    return _public_error_response(request, status.HTTP_403_FORBIDDEN, INSUFFICIENT_PRIVILEGES, accepted_formats)


# Public response when there is no public data available and config file is not provided
NO_PUBLIC_DATA_AVAILABLE = {"message": "No public data available."}


def no_public_data(request: Request, accepted_formats: AcceptedDiscoveryResponseFormats = frozenset(("json",))):
    return _public_error_response(request, status.HTTP_404_NOT_FOUND, NO_PUBLIC_DATA_AVAILABLE, accepted_formats)


# Public response when public fields are not configured and config file is not provided
NO_PUBLIC_FIELDS_CONFIGURED = {"message": "No public fields configured."}


def no_public_fields(request: Request, accepted_formats: AcceptedDiscoveryResponseFormats = frozenset(("json",))):
    return _public_error_response(request, status.HTTP_404_NOT_FOUND, NO_PUBLIC_FIELDS_CONFIGURED, accepted_formats)


def csv_or_json_error_response(
    request: Request, bento_error_dict: dict, accepted_formats: AcceptedDiscoveryResponseFormats
) -> Response:
    """
    Given a Bento JSON-format error response dictionary, either keep it as-is (if JSON is accepted or we need
    to return *something*), or reformat it as a CSV response (if CSV is accepted, e.g., in discovery matches).
    """

    authz_middleware.mark_authz_done(request)  # may have already been done if endpoint has BentoAllowAny permissions

    if "json" in accepted_formats or "csv" not in accepted_formats:
        # If the client wants/can accept JSON (or at the very least cannot accept CSV), return our response as-is.
        return Response(bento_error_dict, status=bento_error_dict["code"])

    # otherwise, return csv error (for discovery matches endpoint)

    field_names = ["code", "message", "timestamp"]
    csv_row = {
        "code": str(bento_error_dict["code"]),
        "message": bento_error_dict["message"],
        "timestamp": bento_error_dict["timestamp"],
    }
    if "errors" in bento_error_dict:
        field_names.append("errors")
        csv_row["errors"] = json.dumps(bento_error_dict["errors"], indent=None).strip()

    csv_bytes = _error_csv_utf8_bytes(field_names, csv_row)
    return Response(csv_bytes, status=status.HTTP_406_NOT_ACCEPTABLE, content_type="text/csv")


async def django_validation_error(
    request: Request,
    e: ValidationError,
    logger: BoundLogger,
    logger_event: LiteralString,
    accepted_formats: AcceptedDiscoveryResponseFormats = frozenset({"json"}),
):
    """
    Generates a Bento-format bad request error (either JSON or CSV) from a Django ValidationError instance, in addition
    to emitting an INFO-level logger event with a stack trace.
    """

    await logger.ainfo(logger_event, exc=e)
    return csv_or_json_error_response(
        request,
        errors.bad_request_error(*(e.error_list if hasattr(e, "error_list") else e.error_dict.items())),
        accepted_formats,
    )
