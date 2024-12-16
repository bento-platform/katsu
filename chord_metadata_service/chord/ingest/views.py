from __future__ import annotations

import traceback
import uuid

from adrf.decorators import api_view
from asgiref.sync import sync_to_async
from bento_lib.auth.permissions import P_INGEST_DATA
from bento_lib.auth.resources import build_resource
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response
from typing import Any, Callable

from bento_lib.responses import errors

from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.authz.permissions import BentoDeferToHandler
from chord_metadata_service.chord.models import Dataset
from chord_metadata_service.logger import logger
from . import experiments
from . import WORKFLOW_INGEST_FUNCTION_MAP
from .exceptions import IngestError
from ..data_types import DATA_TYPE_EXPERIMENT
from ..workflows.metadata import workflow_set


DATASET_DNE = "Dataset does not exist"


def call_ingest_function_and_handle(fn: Callable[[Any, str], Any], data, dataset_id: str) -> Response:
    try:
        with transaction.atomic():
            # Wrap ingestion in a transaction, so if it fails we don't end up in a partial state in the database.
            fn(data, dataset_id)

    except IngestError as e:
        err = f"Encountered ingest error: {e}\n{traceback.format_exc()}"
        logger.error(err)
        return Response(errors.bad_request_error(err), status=status.HTTP_400_BAD_REQUEST)

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
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([BentoDeferToHandler])
async def ingest_derived_experiment_results(request: DrfRequest, dataset_id: str):
    dataset = await Dataset.objects.filter(identifier=dataset_id).afirst()

    if not dataset:
        logger.error(f"Error encountered while ingesting derived experiment results: {DATASET_DNE}")
        authz_middleware.mark_authz_done(request)
        return Response(errors.bad_request_error(DATASET_DNE), status=status.HTTP_400_BAD_REQUEST)

    if not await authz_middleware.async_evaluate_one(
        request,
        build_resource(str(dataset.project_id), str(dataset.identifier), DATA_TYPE_EXPERIMENT),
        P_INGEST_DATA,
        mark_authz_done=True,
    ):
        return Response(errors.forbidden_error("Forbidden"), status=status.HTTP_403_FORBIDDEN)

    return await sync_to_async(call_ingest_function_and_handle)(
        experiments.ingest_derived_experiment_results, request.data, dataset_id
    )


@api_view(["POST"])
@permission_classes([BentoDeferToHandler])
async def ingest_into_dataset(request: DrfRequest, dataset_id: str, workflow_id: str):
    logger.info(f"Received a {workflow_id} ingest request for dataset {dataset_id}.")

    # Check that the workflow exists
    if workflow_id not in WORKFLOW_INGEST_FUNCTION_MAP:
        err = "Ingestion workflow ID does not exist"
        logger.error(f"Error encountered while ingesting into dataset: {err}")
        authz_middleware.mark_authz_done(request)
        return Response(errors.bad_request_error(err), status=status.HTTP_400_BAD_REQUEST)

    dataset = await Dataset.objects.filter(identifier=dataset_id).afirst()

    if not dataset:
        logger.error(
            f"Error encountered while ingesting into dataset with workflow {workflow_id}: {DATASET_DNE}")
        authz_middleware.mark_authz_done(request)
        return Response(errors.bad_request_error(DATASET_DNE), status=status.HTTP_400_BAD_REQUEST)

    workflow = workflow_set.get_workflow(workflow_id)

    dataset_id = str(uuid.UUID(dataset_id))  # Normalize dataset ID to UUID's str format.
    if not (
        await authz_middleware.async_evaluate_one(
            request,
            build_resource(str(dataset.project_id), dataset_id, workflow.data_type),
            P_INGEST_DATA,
            mark_authz_done=True,
        )
    ):
        return Response(errors.forbidden_error("Forbidden"), status=status.HTTP_403_FORBIDDEN)

    return await sync_to_async(call_ingest_function_and_handle)(
        WORKFLOW_INGEST_FUNCTION_MAP[workflow_id], request.data, dataset_id
    )
