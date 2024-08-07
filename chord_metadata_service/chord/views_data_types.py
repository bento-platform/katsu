import asyncio

from bento_lib.auth.permissions import P_DELETE_DATA
from bento_lib.auth.resources import build_resource
from bento_lib.responses import errors
from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from adrf.decorators import api_view
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response

from typing import Callable

from chord_metadata_service.authz.middleware import authz_middleware as authz
from chord_metadata_service.authz.permissions import BentoAllowAny, BentoDeferToHandler
from chord_metadata_service.authz.types import DataPermissionsDict
from chord_metadata_service.discovery.censorship import thresholded_count
from chord_metadata_service.discovery.types import DiscoveryConfig
from chord_metadata_service.discovery.utils import (
    get_discovery,
    get_project_id_and_dataset_id_from_request,
    get_request_discovery,
    get_discovery_data_type_permissions,
)
from chord_metadata_service.chord.models import Dataset, Project
from chord_metadata_service.cleanup import run_all_cleanup
from chord_metadata_service.experiments.models import Experiment
from chord_metadata_service.logger import logger
from chord_metadata_service.phenopackets.models import Phenopacket

from . import data_types as dt

QUERYSET_FN: dict[str, Callable] = {
    dt.DATA_TYPE_EXPERIMENT: lambda dataset_id: Experiment.objects.filter(dataset_id=dataset_id),
    dt.DATA_TYPE_PHENOPACKET: lambda dataset_id: Phenopacket.objects.filter(dataset_id=dataset_id),
}


async def _filtered_query(data_type: str, project: str | None = None, dataset: str | None = None) -> QuerySet:
    """
    Returns a filtered query based on the data type, project, and dataset.
    """

    q: QuerySet | None = None

    if data_type in (dt.DATA_TYPE_PHENOPACKET, dt.DATA_TYPE_EXPERIMENT):
        q = (Phenopacket if data_type == dt.DATA_TYPE_PHENOPACKET else Experiment).objects.all()
        if dataset:
            try:
                q = q.filter(dataset_id=dataset)
            except ValidationError:
                raise ValueError("Dataset ID must be a UUID")
        elif project:
            try:
                q = q.filter(dataset__project_id=project)
            except ValidationError:
                raise ValueError("Project ID must be a UUID")

    if q is None:
        raise ValueError(f"Unsupported data type: {data_type}")

    return q


async def get_count_for_data_type(
    data_type: str,
    project: str | None,
    dataset: str | None,
    discovery: DiscoveryConfig,
    permissions: DataPermissionsDict,
) -> int | None:
    """
    Returns the count for a particular data type. If dataset is provided, project will be ignored. If neither are
    provided, the count will be for the whole node.
    """
    q = await _filtered_query(data_type, project, dataset)
    return None if q is None else thresholded_count(await q.acount(), discovery, permissions)


async def get_last_ingested_for_data_type(data_type: str, project: str | None = None,
                                          dataset: str | None = None) -> dict | None:

    q = await _filtered_query(data_type, project, dataset)
    if q is None:
        return None
    latest_obj = await q.order_by('-created').afirst()

    if not latest_obj:
        return None

    return latest_obj.created


async def make_data_type_response_object(
    data_type_id: str,
    data_type_details: dict,
    project: str | None,
    dataset: str | None,
    discovery: DiscoveryConfig,
    permissions: DataPermissionsDict,
) -> dict:
    return {
        **data_type_details,
        "id": data_type_id,
        **(
            {"count": await get_count_for_data_type(data_type_id, project, dataset, discovery, permissions)}
            if permissions["counts"] else {}
        ),
        "last_ingested": await get_last_ingested_for_data_type(data_type_id, project, dataset)
    }


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def data_type_list(request: DrfRequest):
    # TODO: Permissions: only return counts when we are authenticated/have access to counts or full data.

    project_id, dataset_id = get_project_id_and_dataset_id_from_request(request)

    try:
        discovery, dt_permissions = await asyncio.gather(
            get_request_discovery(request), get_discovery_data_type_permissions(request)
        )
    except ValidationError as e:  # invalid UUID as ID
        return Response(errors.bad_request_error(str(e)), status=status.HTTP_400_BAD_REQUEST)

    dt_response = []
    for dt_id, dt_d in dt.DATA_TYPES.items():
        try:
            dt_response.append(
                await make_data_type_response_object(
                    dt_id, dt_d, project_id, dataset_id, discovery, dt_permissions[dt_id]
                )
            )
        except ValueError as e:  # TODO: from where?
            return Response(errors.bad_request_error(str(e)), status=status.HTTP_400_BAD_REQUEST)

    dt_response.sort(key=lambda d: d["id"])
    return Response(dt_response)


def bad_request_from_exc(e: Exception) -> Response:
    return Response(errors.bad_request_error(str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def data_type_detail(request: DrfRequest, data_type: str):
    # TODO: Permissions: only return counts when we are authenticated/have access to counts or full data.

    if data_type not in dt.DATA_TYPES:
        return Response(errors.not_found_error(f"Data type {data_type} not found"), status=status.HTTP_404_NOT_FOUND)

    project_id, dataset_id = get_project_id_and_dataset_id_from_request(request)

    try:
        # TODO: just get the one data type
        discovery, dt_permissions = await asyncio.gather(
            get_request_discovery(request), get_discovery_data_type_permissions(request)
        )
    except ValidationError as e:  # UUID most likely
        return bad_request_from_exc(e)

    try:
        return Response(
            await make_data_type_response_object(
                data_type, dt.DATA_TYPES[data_type], project_id, dataset_id, discovery, dt_permissions[data_type]
            )
        )
    except ValueError as e:  # TODO: from what
        return bad_request_from_exc(e)


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def data_type_schema(_request: DrfRequest, data_type: str):
    # TODO: exclude extra_properties schema
    if data_type not in dt.DATA_TYPES:
        return Response(errors.not_found_error(f"Data type {data_type} not found"), status=status.HTTP_404_NOT_FOUND)

    return Response(dt.DATA_TYPES[data_type]["schema"])


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def data_type_metadata_schema(_request: DrfRequest, data_type: str):
    if data_type not in dt.DATA_TYPES:
        return Response(errors.not_found_error(f"Data type {data_type} not found"), status=status.HTTP_404_NOT_FOUND)

    return Response(dt.DATA_TYPES[data_type]["metadata_schema"])


@api_view(["GET", "DELETE"])
@permission_classes([BentoDeferToHandler])
async def dataset_data_type(request: DrfRequest, dataset_id: str, data_type: str):
    dataset = await Dataset.objects.aget(identifier=dataset_id)
    project = await Project.objects.aget(datasets=dataset)
    project_id = str(project.identifier)

    if data_type not in QUERYSET_FN:
        authz.mark_authz_done(request)
        return Response(
            errors.bad_request_error(f"Data type {data_type} doesn't exist"), status=status.HTTP_400_BAD_REQUEST)

    qs = QUERYSET_FN[data_type](dataset_id)

    if request.method == "DELETE":
        if not (
            await authz.async_evaluate_one(request, build_resource(project_id, dataset_id, data_type), P_DELETE_DATA)
        ):
            authz.mark_authz_done(request)
            return Response(errors.forbidden_error(), status=status.HTTP_403_FORBIDDEN)

        authz.mark_authz_done(request)

        await qs.adelete()

        logger.info(f"Running cleanup after clearing data type {data_type} in dataset {dataset_id} via API")
        n_removed = await run_all_cleanup()
        logger.info(f"Cleanup: removed {n_removed} objects in total")

        return Response(status=status.HTTP_204_NO_CONTENT)

    discovery = await get_discovery(project_id, dataset_id)
    dt_permissions = await get_discovery_data_type_permissions(request, project_id, dataset_id)

    response_object = await make_data_type_response_object(
        data_type,
        dt.DATA_TYPES[data_type],
        project=str(project.identifier),
        dataset=dataset_id,
        discovery=discovery,
        permissions=dt_permissions[data_type],
    )

    authz.mark_authz_done(request)
    return Response(response_object)


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def dataset_datatype_summary(request: DrfRequest, dataset_id: str):
    dataset = await Dataset.objects.aget(identifier=dataset_id)
    project = await Project.objects.aget(datasets=dataset)
    project_id = str(project.identifier)

    try:
        discovery = await get_discovery(project_id, dataset_id)
    except ValidationError as e:
        return bad_request_from_exc(e)

    dt_permissions = await get_discovery_data_type_permissions(request, project_id, dataset_id)

    dt_response = []
    for dt_id, dt_d in dt.DATA_TYPES.items():
        try:
            dt_response.append(
                await make_data_type_response_object(
                    dt_id, dt_d, project_id, dataset_id, discovery, dt_permissions[dt_id]
                )
            )
        except ValueError as e:
            return Response(errors.bad_request_error(str(e)), status=status.HTTP_400_BAD_REQUEST)

    dt_response.sort(key=lambda d: d["id"])
    return Response(dt_response)
