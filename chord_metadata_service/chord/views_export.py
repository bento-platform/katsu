import json
import logging
import traceback

from django.http import FileResponse

from jsonschema import Draft7Validator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.request import Request


from chord_metadata_service.chord.schemas import EXPORT_SCHEMA
from bento_lib.responses import errors

from .export import EXPORT_FORMAT_FUNCTION_MAP, EXPORT_FORMAT_OBJECT_TYPE_MAP, EXPORT_FORMATS, EXPORT_OBJECT_TYPE
from .export_utils import ExportError, ExportFileContext


BENTO_EXPORT_SCHEMA_VALIDATOR = Draft7Validator(EXPORT_SCHEMA)

logger = logging.getLogger(__name__)


# Mounted on /private/, so will get protected anyway; this allows for access from WES
# TODO: Ugly and misleading permissions
@api_view(["POST"])
@permission_classes([AllowAny])
def export(request: Request):
    """Export data from Katsu

    Exports the requested data object (e.g. a Dataset or a Project) in the given
    format.
    Note that the generated files will be either written locally if a path is
    provided, or downloaded as a tar gzipped attachment otherwise.

    Args:
        request: Django Rest Framework request object. The data property contains
        the payload as a JSON following the export schema.
    """
    # Private endpoints are protected by URL namespace, not by Django permissions.

    # TODO: Schema for OpenAPI doc

    logger.info(f"Received export request: {json.dumps(request.data)}")

    if not BENTO_EXPORT_SCHEMA_VALIDATOR.is_valid(request.data):
        msg_list = [err.message for err in BENTO_EXPORT_SCHEMA_VALIDATOR.iter_errors(request.data)]
        return Response(errors.bad_request_error(
            "Invalid ingest request body: " + "\n".join(msg_list)),
            status=400  # TODO: Validation errors
        )

    object_id = request.data["object_id"]
    object_type: str = request.data["object_type"]   # 'dataset', 'table',...

    model = EXPORT_OBJECT_TYPE[object_type]["model"]
    if not model.objects.filter(identifier=object_id).exists():
        return Response(errors.bad_request_error(
            f"{object_type.capitalize()} with ID {object_id} does not exist"),
            status=400
        )

    format = request.data["format"].strip()
    output_path = request.data.get("output_path")   # optional parameter

    if format not in EXPORT_FORMATS:  # Check that the workflow exists
        return Response(errors.bad_request_error(
            f"Export in format {format} is not implemented"),
            status=400
        )

    if object_type not in EXPORT_FORMAT_OBJECT_TYPE_MAP[format]:
        return Response(errors.bad_request_error(
            f"Exporting entities of type {object_type} in format {format} is not implemented"),
             status=400
        )

    # TODO: secure the output_path value

    try:
        with ExportFileContext(output_path, object_id) as file_export:
            # Pass a callable to generate the proper file paths within the export context.
            EXPORT_FORMAT_FUNCTION_MAP[format](file_export.get_path, object_id)

            # If no output path parameter has been provided, the generated export
            # is returned as an attachment to the Response and everything will
            # be cleaned afterwards.
            # Otherwise, the provided local path is under the responsability of
            # the caller
            if not output_path:
                tarfile = file_export.write_tar()
                return FileResponse(open(tarfile, "rb"), as_attachment=True)

    except ExportError as e:
        return Response(errors.bad_request_error(f"Encountered export error: {e}"), status=400)

    except Exception as e:
        # Encountered some other error from the export attempt, return a somewhat detailed message
        logger.error(f"Encountered an exception while processing an export attempt:\n{traceback.format_exc()}")
        return Response(errors.internal_server_error(
            f"Encountered an exception while processing an export attempt (error: {repr(e)}"),
            status=500
        )

    return Response(status=204)
