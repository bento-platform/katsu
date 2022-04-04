import json
import logging
import traceback
import uuid

# Can't because code expects `ingestion` namespace
#from jsonschema import Draft7Validator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


# Can't because code expects `ingestion` namespace
#from bento_lib.schemas.bento import BENTO_INGEST_SCHEMA
from bento_lib.responses import errors
#from bento_lib.workflows import get_workflow, get_workflow_resource, workflow_exists

from .export import WORKFLOW_EXPORT_FUNCTION_MAP
from .export_utils import ExportError

from .ingest import METADATA_WORKFLOWS
from .models import Dataset, Table


# Can't because code expects `ingestion` namespace
#BENTO_INGEST_SCHEMA_VALIDATOR = Draft7Validator(BENTO_INGEST_SCHEMA)

logger = logging.getLogger(__name__)


# Mounted on /private/, so will get protected anyway; this allows for access from WES
# TODO: Ugly and misleading permissions
@api_view(["POST"])
@permission_classes([AllowAny])
def export(request):
    # Export data from Katsu.
    # Private endpoints are protected by URL namespace, not by Django permissions.

    # TODO: Schema for OpenAPI doc

    logger.info(f"Received export request: {json.dumps(request.data)}")

    # Can't because code expects `ingestion` namespace
    # if not BENTO_INGEST_SCHEMA_VALIDATOR.is_valid(request.data):
    #     return Response(errors.bad_request_error("Invalid ingest request body"), status=400)  # TODO: Validation errors

    object_id = request.data["object_id"]
    object_type = request.data["object_type"]   # 'dataset', 'table',...

    if (object_type == 'table' 
        and not Table.objects.filter(ownership_record_id=object_id).exists()):
        return Response(errors.bad_request_error(f"Table with ID {object_id} does not exist"), status=400)
    elif (object_type == 'dataset' 
        and not Dataset.objects.filter(identifier=object_id).exists()):
        return Response(errors.bad_request_error(f"Dataset with ID {object_id} does not exist"), status=400)
    

    object_id = str(uuid.UUID(object_id))  # Normalize ID to UUID's str format.

    workflow_id = request.data["workflow_id"].strip()
    workflow_exportpath = request.data["workflow_exportpath"]

    if not workflow_id in METADATA_WORKFLOWS.export:  # Check that the workflow exists
        return Response(errors.bad_request_error(f"Workflow with ID {workflow_id} does not exist"), status=400)

    try:
       WORKFLOW_EXPORT_FUNCTION_MAP[workflow_id](workflow_exportpath, object_id)

    except ExportError as e:
        return Response(errors.bad_request_error(f"Encountered export error: {e}"), status=400)


    except Exception as e:
        # Encountered some other error from the export attempt, return a somewhat detailed message
        logger.error(f"Encountered an exception while processing an export attempt:\n{traceback.format_exc()}")
        return Response(errors.internal_server_error(f"Encountered an exception while processing an export attempt "
                                                     f"(error: {repr(e)}"), status=500)

    return Response(status=204)
