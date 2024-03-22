from __future__ import annotations

import traceback
import uuid

from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response
from typing import Any, Callable

from bento_lib.responses import errors

from chord_metadata_service.logger import logger
from chord_metadata_service.chord.models import Dataset
from . import experiments
from . import WORKFLOW_INGEST_FUNCTION_MAP
from .exceptions import IngestError


def call_ingest_function_and_handle(fn: Callable[[Any, str], Any], data, dataset_id: str) -> Response:
    try:
        with transaction.atomic():
            # Wrap ingestion in a transaction, so if it fails we don't end up in a partial state in the database.
            fn(data, dataset_id)

    except IngestError as e:
        err = f"Encountered ingest error: {e}\n{traceback.format_exc()}"
        logger.error(err)
        return Response(errors.bad_request_error(err), status=400)

    except ValidationError as e:
        validation_errors = tuple(e.error_list if hasattr(e, "error_list") else e.error_dict.items())
        logger.error(f"Encountered validation errors during ingestion: {validation_errors}")
        return Response(errors.bad_request_error(
            "Encountered validation errors during ingestion",
            *validation_errors,
        ))

    except Exception as e:
        # Encountered some other error from the ingestion attempt, return a somewhat detailed message
        logger.error(f"Encountered an exception while processing an ingest attempt:\n{traceback.format_exc()}")
        return Response(errors.internal_server_error(f"Encountered an exception while processing an ingest attempt "
                                                     f"(error: {repr(e)}"), status=500)
    return Response(status=204)


@api_view(["POST"])
@permission_classes([AllowAny])
def ingest_derived_experiment_results(request: DrfRequest, dataset_id: str):
    return call_ingest_function_and_handle(experiments.ingest_derived_experiment_results, request.data, dataset_id)


@api_view(["POST"])
@permission_classes([AllowAny])
def ingest_into_dataset(request: DrfRequest, dataset_id: str, workflow_id: str):
    logger.info(f"Received a {workflow_id} ingest request for dataset {dataset_id}.")

    # Check that the workflow exists
    if workflow_id not in WORKFLOW_INGEST_FUNCTION_MAP:
        err = f"Ingestion workflow ID {workflow_id} does not exist"
        logger.error(f"Error encountered while ingesting into dataset {dataset_id}: {err}")
        return Response(errors.bad_request_error(err), status=400)

    if not Dataset.objects.filter(identifier=dataset_id).exists():
        err = f"Dataset with ID {dataset_id} does not exist"
        logger.error(
            f"Error encountered while ingesting into dataset {dataset_id} with workflow {workflow_id}: {err}")
        return Response(errors.bad_request_error(err), status=400)
    dataset_id = str(uuid.UUID(dataset_id))  # Normalize dataset ID to UUID's str format.

    return call_ingest_function_and_handle(WORKFLOW_INGEST_FUNCTION_MAP[workflow_id], request.data, dataset_id)
