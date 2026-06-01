from __future__ import annotations

from adrf.decorators import api_view
from asgiref.sync import sync_to_async
from bento_lib.auth.permissions import P_INGEST_DATA
from bento_lib.auth.resources import build_resource
from django.core.exceptions import ValidationError
from django.db import transaction
from structlog.stdlib import BoundLogger
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response
from typing import Any, Callable

from bento_lib.responses import errors

from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.authz.permissions import BentoDeferToHandler
from chord_metadata_service.chord.models import DatasetV2
from chord_metadata_service.logger import logger
from . import experiments
from . import WORKFLOW_INGEST_FUNCTION_MAP
from .exceptions import IngestError
from ..data_types import DATA_TYPE_EXPERIMENT
from ..workflows.metadata import workflow_set


DATASET_DNE = "dataset does not exist"


@sync_to_async
def call_ingest_function_and_handle(
    fn: Callable[[Any, str, BoundLogger], Any], data, dataset_id: str, lg: BoundLogger
) -> Response:
    try:
        with transaction.atomic():
            # Wrap ingestion in a transaction, so if it fails we don't end up in a partial state in the database.
            fn(data, dataset_id, lg)

    except IngestError as e:
        err = "encountered ingestion error"
        lg.exception(err, exc_info=e)
        return Response(errors.bad_request_error(err), status=status.HTTP_400_BAD_REQUEST)

    except ValidationError as e:
        validation_errors = tuple(e.error_list if hasattr(e, "error_list") else e.error_dict.items())
        err = "encountered validation errors during ingestion"
        lg.exception(err, exc_info=e)
        return Response(errors.bad_request_error(err, *validation_errors), status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # Encountered some other error from the ingestion attempt, return a somewhat detailed message
        err = "encountered an exception while processing an ingest attempt"
        lg.exception(err, exc_info=e)
        return Response(
            errors.internal_server_error(f"{err} (error: {repr(e)})"), status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([BentoDeferToHandler])
async def ingest_derived_experiment_results(request: DrfRequest, dataset_id: str):
    lg = logger.bind(dataset_id=dataset_id)

    dataset = await DatasetV2.objects.filter(identifier=dataset_id).afirst()

    if not dataset:
        lg.error(f"error encountered while ingesting derived experiment results: {DATASET_DNE}")
        authz_middleware.mark_authz_done(request)
        return Response(errors.bad_request_error(DATASET_DNE), status=status.HTTP_400_BAD_REQUEST)

    project_id_str = str(dataset.project_id)
    lg = lg.bind(project_id=project_id_str)

    if not await authz_middleware.async_evaluate_one(
        request,
        build_resource(project_id_str, str(dataset.identifier), DATA_TYPE_EXPERIMENT),
        P_INGEST_DATA,
        mark_authz_done=True,
    ):
        return Response(errors.forbidden_error("Forbidden"), status=status.HTTP_403_FORBIDDEN)

    return await call_ingest_function_and_handle(
        experiments.ingest_derived_experiment_results, request.data, dataset_id, lg
    )


@api_view(["POST"])
@permission_classes([BentoDeferToHandler])
async def ingest_into_dataset(request: DrfRequest, dataset_id: str, workflow_id: str):
    lg = logger.bind(dataset_id=dataset_id, workflow_id=workflow_id)  # bind diagnostic metadata to logger

    lg.info("received ingest request")

    # Check that the workflow exists
    if workflow_id not in WORKFLOW_INGEST_FUNCTION_MAP:
        err = "ingestion workflow ID does not exist"
        lg.error(err)
        authz_middleware.mark_authz_done(request)
        return Response(errors.bad_request_error(err), status=status.HTTP_400_BAD_REQUEST)

    dataset = await DatasetV2.objects.filter(identifier=dataset_id).afirst()

    if not dataset:
        # for logging, make it a bit more clear where this error is coming from
        lg.error(f"error encountered while ingesting: {DATASET_DNE}")
        authz_middleware.mark_authz_done(request)
        return Response(errors.bad_request_error(DATASET_DNE), status=status.HTTP_400_BAD_REQUEST)

    lg = lg.bind(project_id=str(dataset.project_id))

    workflow = workflow_set.get_workflow(workflow_id)

    if not (
        await authz_middleware.async_evaluate_one(
            request,
            build_resource(str(dataset.project_id), dataset_id, workflow.data_type),
            P_INGEST_DATA,
            mark_authz_done=True,
        )
    ):
        return Response(errors.forbidden_error("Forbidden"), status=status.HTTP_403_FORBIDDEN)

    return await call_ingest_function_and_handle(
        WORKFLOW_INGEST_FUNCTION_MAP[workflow_id], request.data, dataset_id, lg
    )
