from adrf.decorators import api_view as async_api_view
from bento_lib.auth.permissions import P_EXPORT_DATA
from bento_lib.auth.resources import RESOURCE_EVERYTHING
from django.http import FileResponse

from jsonschema import Draft7Validator
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.request import Request as DrfRequest

from bento_lib.responses import errors

from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.authz.permissions import BentoDeferToHandler
from chord_metadata_service.chord.schemas import EXPORT_SCHEMA
from chord_metadata_service.logger import logger
from .metadata import EXPORT_FORMAT_FUNCTION_MAP, EXPORT_FORMAT_OBJECT_TYPE_MAP, EXPORT_FORMATS, EXPORT_OBJECT_TYPE
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

    res = await authz_middleware.async_evaluate_one(request, RESOURCE_EVERYTHING, P_EXPORT_DATA, mark_authz_done=True)
    if not res:
        return Response(errors.forbidden_error("Fobidden"), status=status.HTTP_403_FORBIDDEN)

    # TODO: Schema for OpenAPI doc

    await logger.ainfo("received export request", request_data=request.data)

    if not BENTO_EXPORT_SCHEMA_VALIDATOR.is_valid(request.data):
        msg_list = [err.message for err in BENTO_EXPORT_SCHEMA_VALIDATOR.iter_errors(request.data)]
        return Response(errors.bad_request_error(
            "Invalid export request body: " + "\n".join(msg_list)),
            status=400  # TODO: Validation errors
        )

    object_id = request.data["object_id"]
    object_type: str = request.data["object_type"]   # 'project', 'dataset',...

    model = EXPORT_OBJECT_TYPE[object_type]["model"]
    if not await model.objects.filter(identifier=object_id).aexists():
        return Response(errors.bad_request_error(
            f"{object_type.capitalize()} with ID {object_id} does not exist"),
            status=status.HTTP_400_BAD_REQUEST,
        )

    fmt = request.data["format"].strip()
    output_path = request.data.get("output_path")   # optional parameter

    if fmt not in EXPORT_FORMATS:  # Check that the workflow exists
        return Response(errors.bad_request_error(
            f"Export in format {fmt} is not implemented"),
            status=status.HTTP_400_BAD_REQUEST,
        )

    if object_type not in EXPORT_FORMAT_OBJECT_TYPE_MAP[fmt]:
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
        await logger.aexception("encountered export error", exc_info=e)
        return Response(errors.bad_request_error(f"Encountered export error: {e}"), status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # Encountered some other error from the export attempt, return a somewhat detailed message
        err_msg = "encountered exception while processing export attempt"
        await logger.aexception(err_msg, exc_info=e)
        return Response(errors.internal_server_error(
            f"{err_msg} (error: {repr(e)}"),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(status=status.HTTP_204_NO_CONTENT)
