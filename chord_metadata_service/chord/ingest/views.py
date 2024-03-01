from __future__ import annotations

import logging
import traceback
import uuid

from bento_lib.responses import errors
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from . import WORKFLOW_INGEST_FUNCTION_MAP
from .exceptions import IngestError
from ..models import Dataset


FROM_DERIVED_DATA = "FROM_DERIVED_DATA"
DATASET_ID_OVERRIDES = {FROM_DERIVED_DATA}    # These special values skip the checks on the table

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([AllowAny])
def ingest_into_dataset(request, dataset_id: str, workflow_id: str):
    logger.info(f"Received a {workflow_id} ingest request for dataset {dataset_id}.")

    # Check that the workflow exists
    if workflow_id not in WORKFLOW_INGEST_FUNCTION_MAP:
        return Response(errors.bad_request_error(f"Ingestion workflow ID {workflow_id} does not exist"), status=400)

    if dataset_id not in DATASET_ID_OVERRIDES:
        if not Dataset.objects.filter(identifier=dataset_id).exists():
            return Response(errors.bad_request_error(f"Dataset with ID {dataset_id} does not exist"), status=400)
        dataset_id = str(uuid.UUID(dataset_id))  # Normalize dataset ID to UUID's str format.

    try:
        with transaction.atomic():
            # Wrap ingestion in a transaction, so if it fails we don't end up in a partial state in the database.
            WORKFLOW_INGEST_FUNCTION_MAP[workflow_id](request.data, dataset_id)

    except IngestError as e:
        return Response(errors.bad_request_error(f"Encountered ingest error: {e}"), status=400)

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
    return Response(status=204)
