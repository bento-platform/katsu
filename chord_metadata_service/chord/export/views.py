from adrf.decorators import api_view as async_api_view
from bento_lib.auth.permissions import P_EXPORT_DATA
from bento_lib.auth.resources import RESOURCE_EVERYTHING
from bento_lib.responses import errors
from django.http import FileResponse
from jsonschema import Draft7Validator
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.request import Request as DrfRequest
from structlog.stdlib import BoundLogger

from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.authz.permissions import BentoDeferToHandler
from chord_metadata_service.chord.schemas import EXPORT_SCHEMA
from chord_metadata_service.logger import logger
from .metadata import EXPORT_FORMAT_FUNCTION_MAP, EXPORT_FORMAT_OBJECT_TYPE_MAP, EXPORT_OBJECT_TYPE
from .utils import ExportError, ExportFileContext

BENTO_EXPORT_SCHEMA_VALIDATOR = Draft7Validator(EXPORT_SCHEMA)


@async_api_view(["POST"])
@permission_classes([BentoDeferToHandler])
async def export(request: DrfRequest):
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

    lg: BoundLogger = logger

    res = await authz_middleware.async_evaluate_one(request, RESOURCE_EVERYTHING, P_EXPORT_DATA, mark_authz_done=True)
    if not res:
        return Response(errors.forbidden_error("Forbidden"), status=status.HTTP_403_FORBIDDEN)

    # TODO: Schema for OpenAPI doc

    await lg.ainfo("received export request", request_data=request.data)

    if not BENTO_EXPORT_SCHEMA_VALIDATOR.is_valid(request.data):
        msg_list = [err.message for err in BENTO_EXPORT_SCHEMA_VALIDATOR.iter_errors(request.data)]
        await lg.aerror("invalid export request body", errors=msg_list)
        return Response(errors.bad_request_error(
            "Invalid export request body: " + "\n".join(msg_list)),
            status=status.HTTP_400_BAD_REQUEST
        )

    object_id = request.data["object_id"]
    object_type: str = request.data["object_type"]   # 'project', 'dataset',...

    lg = lg.bind(object_type=object_type)  # don't bind object ID yet to prevent log injection

    model = EXPORT_OBJECT_TYPE[object_type]["model"]
    if not await model.objects.filter(identifier=object_id).aexists():
        await lg.aerror("object with ID does not exist")
        return Response(errors.bad_request_error(
            f"{object_type.capitalize()} with ID {object_id} does not exist"),
            status=status.HTTP_400_BAD_REQUEST,
        )

    fmt = request.data["format"].strip()
    output_path = request.data.get("output_path")   # optional parameter

    lg = lg.bind(output_format=fmt)

    # Don't need to check that format is correct, because the schema enum for the field has already taken care of it.

    if object_type not in EXPORT_FORMAT_OBJECT_TYPE_MAP[fmt]:
        await lg.aerror("exporting entities of specified type in specified format: not implemented")
        return Response(errors.bad_request_error(
            f"Exporting entities of type {object_type} in format {fmt} is not implemented"),
             status=status.HTTP_400_BAD_REQUEST,
        )

    # TODO: secure the output_path value

    try:
        with ExportFileContext(output_path, object_id) as file_export:
            # Pass a callable to generate the proper file paths within the export context.
            await EXPORT_FORMAT_FUNCTION_MAP[fmt](file_export.get_path, object_id)

            # If no output path parameter has been provided, the generated export
            # is returned as an attachment to the Response and everything will
            # be cleaned afterward.
            # Otherwise, the provided local path is under the responsibility of
            # the caller
            if not output_path:
                tarfile = file_export.write_tar()
                # No context manager needed; Django will close it automatically.
                return FileResponse(open(tarfile, "rb"), as_attachment=True)

    except ExportError as e:
        await lg.aexception("encountered export error", exc_info=e)
        return Response(errors.bad_request_error(f"Encountered export error: {e}"), status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # Encountered some other error from the export attempt, return a somewhat detailed message
        err_msg = "encountered exception while processing export attempt"
        await lg.aexception(err_msg, exc_info=e)
        return Response(errors.internal_server_error(
            f"{err_msg} (error: {repr(e)}"),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(status=status.HTTP_204_NO_CONTENT)
