from __future__ import annotations

import json
import logging
import traceback
import uuid

from django.core.exceptions import ValidationError
from django.db import transaction
from jsonschema import Draft7Validator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from bento_lib.schemas.bento import BENTO_INGEST_SCHEMA
from bento_lib.responses import errors
from bento_lib.workflows import workflow_exists

from . import WORKFLOW_INGEST_FUNCTION_MAP
from .exceptions import IngestError
from ..models import Table
from ..workflows.metadata import METADATA_WORKFLOWS


BENTO_INGEST_SCHEMA_VALIDATOR = Draft7Validator(BENTO_INGEST_SCHEMA)
FROM_DERIVED_DATA = "FROM_DERIVED_DATA"
TABLE_ID_OVERRIDES = {FROM_DERIVED_DATA}    # These special values skip the checks on the table

logger = logging.getLogger(__name__)


# Mounted on /private/, so will get protected anyway; this allows for access from WES
# TODO: Ugly and misleading permissions
@api_view(["POST"])
@permission_classes([AllowAny])
def ingest(request):
    # Private ingest endpoints are protected by URL namespace, not by Django permissions.

    # TODO: Schema for OpenAPI doc
    # TODO: Use serializers with basic objects and maybe some more complex ones too (but for performance, this might
    #  not be optimal...)

    logger.info(f"Received ingest request: {json.dumps(request.data)}")

    if not BENTO_INGEST_SCHEMA_VALIDATOR.is_valid(request.data):
        return Response(errors.bad_request_error("Invalid ingest request body"), status=400)  # TODO: Validation errors

    table_id = request.data["table_id"]

    if table_id not in TABLE_ID_OVERRIDES:
        if not Table.objects.filter(ownership_record_id=table_id).exists():
            return Response(errors.bad_request_error(f"Table with ID {table_id} does not exist"), status=400)

        table_id = str(uuid.UUID(table_id))  # Normalize dataset ID to UUID's str format.

    workflow_id = request.data["workflow_id"].strip()
    workflow_outputs = request.data["workflow_outputs"]

    if not workflow_exists(workflow_id, METADATA_WORKFLOWS):  # Check that the workflow exists
        return Response(errors.bad_request_error(f"Workflow with ID {workflow_id} does not exist"), status=400)

    try:
        with transaction.atomic():
            # Wrap ingestion in a transaction, so if it fails we don't end up in a partial state in the database.
            WORKFLOW_INGEST_FUNCTION_MAP[workflow_id](workflow_outputs, table_id)

    except IngestError as e:
        return Response(errors.bad_request_error(f"Encountered ingest error: {e}"), status=400)

    except json.decoder.JSONDecodeError as e:
        return Response(errors.bad_request_error(f"Invalid JSON provided for ingest document (message: {e})"),
                        status=400)

    except ValidationError as e:
        return Response(errors.bad_request_error(
            "Encountered validation errors during ingestion",
            *(e.error_list if hasattr(e, "error_list") else e.error_dict.items()),
        ))

    except Exception as e:
        # Encountered some other error from the ingestion attempt, return a somewhat detailed message
        logger.error(f"Encountered an exception while processing an ingest attempt:\n{traceback.format_exc()}")
        return Response(errors.internal_server_error(f"Encountered an exception while processing an ingest attempt "
                                                     f"(error: {repr(e)}"), status=500)

    # TODO: Schema validation
    # TODO: Rollback in case of failures
    return Response(status=204)
