from __future__ import annotations

import logging
import traceback
import uuid

from django.core.exceptions import ValidationError
from django.db import transaction
from jsonschema import Draft7Validator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from typing import List

from bento_lib.schemas.bento import BENTO_INGEST_SCHEMA

from . import WORKFLOW_INGEST_FUNCTION_MAP
from .exceptions import IngestError
from ..models import Dataset


BENTO_INGEST_SCHEMA_VALIDATOR = Draft7Validator(BENTO_INGEST_SCHEMA)
FROM_DERIVED_DATA = "FROM_DERIVED_DATA"
DATASET_ID_OVERRIDES = {FROM_DERIVED_DATA}    # These special values skip the checks on the table

logger = logging.getLogger(__name__)


class IngestResponseBuilder:

    def __init__(self, workflow_id: str, dataset_id: str):
        self.workflow_id = workflow_id
        self.dataset_id = dataset_id
        self.success = False
        self.errors = []
        self.warnings = []

    def set_success(self, success: bool):
        self.success = success

    def add_error(self, error):
        self.errors.append(error)

    def add_errors(self, errors: List):
        self.errors.extend(errors)

    def add_ingest_error(self, error: IngestError):
        if error.validation_errors:
            self.add_errors(error.validation_errors)
        else:
            self.add_error(error.message)

        if error.schema_warnings:
            self.warnings.extend(error.schema_warnings)

    def as_response(self, status_code: int) -> Response:
        body = {
            "success": self.success,
            "warnings": self.warnings,
            "errors": self.errors,
        }
        logger.info(f"Finished {self.workflow_id} ingest request for dataset {self.dataset_id}", body)
        return Response(body, status=status_code)


@api_view(["POST"])
@permission_classes([AllowAny])
def ingest_into_dataset(request, dataset_id: str, workflow_id: str):
    logger.info(f"Received a {workflow_id} ingest request for dataset {dataset_id}.")

    response_builder = IngestResponseBuilder(workflow_id=workflow_id, dataset_id=dataset_id)

    # Check that the workflow exists
    if workflow_id not in WORKFLOW_INGEST_FUNCTION_MAP:
        response_builder.add_error(f"Ingestion workflow ID {workflow_id} does not exist")
        return response_builder.as_response(400)

    if dataset_id not in DATASET_ID_OVERRIDES:
        if not Dataset.objects.filter(identifier=dataset_id).exists():
            response_builder.add_error(f"Dataset with ID {dataset_id} does not exist")
            return response_builder.as_response(400)
        dataset_id = str(uuid.UUID(dataset_id))  # Normalize dataset ID to UUID's str format.

    try:
        with transaction.atomic():
            # Wrap ingestion in a transaction, so if it fails we don't end up in a partial state in the database.
            WORKFLOW_INGEST_FUNCTION_MAP[workflow_id](request.data, dataset_id)

    except IngestError as e:
        response_builder.add_ingest_error(e)
        return response_builder.as_response(400)

    except ValidationError as e:
        response_builder.add_errors(e.error_list if hasattr(e, "error_list") else e.error_dict.items())
        return response_builder.as_response(400)

    except Exception as e:
        # Encountered some other error from the ingestion attempt, return a somewhat detailed message
        logger.error(f"Encountered an exception while processing an ingest attempt:\n{traceback.format_exc()}")
        response_builder.add_error(f"Encountered an exception while processing an ingest attempt (error: {repr(e)})")
        return response_builder.as_response(500)

    response_builder.set_success(True)
    return response_builder.as_response(201)
