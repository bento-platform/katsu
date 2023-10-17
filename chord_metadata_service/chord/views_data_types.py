from bento_lib.responses import errors
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpRequest

from adrf.decorators import api_view
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.response import Response

from typing import Callable

from chord_metadata_service.chord.models import Dataset, Project
from chord_metadata_service.chord.permissions import BentoAllowAny
from chord_metadata_service.cleanup import run_all_cleanup
from chord_metadata_service.experiments.models import Experiment, ExperimentResult
from chord_metadata_service.logger import logger
from chord_metadata_service.metadata.authz import authz_middleware
from chord_metadata_service.mcode.models import MCodePacket
from chord_metadata_service.phenopackets.models import Phenopacket

from . import data_types as dt

QUERYSET_FN: dict[str, Callable] = {
    dt.DATA_TYPE_EXPERIMENT: lambda dataset_id: Experiment.objects.filter(dataset_id=dataset_id),
    dt.DATA_TYPE_MCODEPACKET: lambda dataset_id: MCodePacket.objects.filter(dataset_id=dataset_id),
    dt.DATA_TYPE_PHENOPACKET: lambda dataset_id: Phenopacket.objects.filter(dataset_id=dataset_id),
    dt.DATA_TYPE_EXPERIMENT_RESULT: lambda dataset_id: ExperimentResult.objects.filter(
        experiment__dataset_id=dataset_id),
}


async def get_count_for_data_type(data_type: str, project: str | None = None, dataset: str | None = None) -> int | None:
    """
    Returns the count for a particular data type. If dataset is provided, project will be ignored. If neither are
    provided, the count will be for the whole node.
    """

    if data_type == dt.DATA_TYPE_READSET:
        # No counts for readset, it's a fake data type inside Katsu...
        return None

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

    elif data_type == dt.DATA_TYPE_EXPERIMENT_RESULT:
        q = ExperimentResult.objects.all()
        if dataset:
            try:
                q = q.filter(experiment__dataset_id=dataset)
            except ValidationError:
                raise ValueError("Dataset ID must be a UUID")
        elif project:
            try:
                q = q.filter(experiment__dataset__project_id=project)
            except ValidationError:
                raise ValueError("Project ID must be a UUID")

    if q is None:
        raise ValueError(f"Unsupported data type for count function: {data_type}")

    return await q.acount()


async def make_data_type_response_object(
    data_type_id: str,
    data_type_details: dict,
    project: str | None,
    dataset: str | None,
    include_counts: bool = False,
) -> dict:
    res = {**data_type_details, "id": data_type_id}
    if include_counts:
        res["count"] = await get_count_for_data_type(data_type_id, project, dataset)
    return res


RESOURCE_EVERYTHING = {"everything": True}
PERMISSION_QUERY_DATA = "query:data"


def get_counts_permission(dataset_level: bool) -> str:
    if dataset_level:
        return "query:dataset_level_counts"
    return "query:project_level_counts"  # TODO: we don't have a node-level counts permission


async def can_see_counts(request: HttpRequest, resource: dict) -> bool:
    return await authz_middleware.async_authz_post(request, "/policy/evaluate", {
        "requested_resource": resource,
        "required_permissions": [get_counts_permission(resource.get("dataset") is not None)],
    })["result"] or (
        # If we don't have a count permission, we may still have a query:data permission (no cascade)
        await authz_middleware.async_authz_post(request, "/policy/evaluate", {
            "requested_resource": resource,
            "required_permissions": [PERMISSION_QUERY_DATA],
        })["result"]
    )


def create_resource(project: str | None, dataset: str | None, data_type: str | None) -> dict:
    resource = RESOURCE_EVERYTHING
    if project:
        resource = {"project": project}
        if dataset:
            resource["dataset"] = dataset
        if data_type:
            resource["data_type"] = data_type
    return resource


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def data_type_list(request: HttpRequest):
    # TODO: Permissions: only return counts when we are authenticated/have access to counts or full data.

    project = request.GET.get("project", "").strip() or None
    dataset = request.GET.get("dataset", "").strip() or None

    has_permission: bool = await can_see_counts(request, create_resource(project, dataset, None))

    dt_response = []
    for dt_id, dt_d in dt.DATA_TYPES.items():
        try:
            has_dt_permission: bool = has_permission or (
                await can_see_counts(request, create_resource(project, dataset, dt_id)))
            dt_response.append(
                await make_data_type_response_object(dt_id, dt_d, project, dataset, include_counts=has_dt_permission))
        except ValueError as e:
            return Response(errors.bad_request_error(str(e)), status=status.HTTP_400_BAD_REQUEST)

    dt_response.sort(key=lambda d: d["id"])
    return Response(dt_response)


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def data_type_detail(request: HttpRequest, data_type: str):
    if data_type not in dt.DATA_TYPES:
        return Response(errors.not_found_error(f"Data type {data_type} not found"), status=status.HTTP_404_NOT_FOUND)

    project = request.GET.get("project", "").strip() or None
    dataset = request.GET.get("dataset", "").strip() or None

    try:
        return Response(
            await make_data_type_response_object(
                data_type,
                dt.DATA_TYPES[data_type],
                project,
                dataset,
                include_counts=await can_see_counts(request, create_resource(project, dataset, data_type)),
            ))
    except ValueError as e:
        return Response(errors.bad_request_error(str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def data_type_schema(_request: HttpRequest, data_type: str):
    if data_type not in dt.DATA_TYPES:
        return Response(errors.not_found_error(f"Data type {data_type} not found"), status=status.HTTP_404_NOT_FOUND)

    return Response(dt.DATA_TYPES[data_type]["schema"])


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def data_type_metadata_schema(_request: HttpRequest, data_type: str):
    if data_type not in dt.DATA_TYPES:
        return Response(errors.not_found_error(f"Data type {data_type} not found"), status=status.HTTP_404_NOT_FOUND)

    return Response(dt.DATA_TYPES[data_type]["metadata_schema"])


@api_view(["GET", "DELETE"])
async def dataset_data_type(request: HttpRequest, dataset_id: str, data_type: str):
    if data_type not in QUERYSET_FN:
        authz_middleware.mark_authz_done(request)
        return Response(errors.bad_request_error, status=status.HTTP_400_BAD_REQUEST)

    project = await Project.objects.aget(datasets=dataset_id)
    resource = create_resource(project.identifier, dataset_id, data_type)

    qs = QUERYSET_FN[data_type](dataset_id)

    if request.method == "DELETE":
        has_permission: bool = await authz_middleware.async_authz_post(request, "/permissions/evaluate", {
            "requested_resource": resource,
            "required_permissions": ["delete:data"],
        })
        authz_middleware.mark_authz_done(request)

        if not has_permission:
            return Response(errors.forbidden_error, status=status.HTTP_403_FORBIDDEN)

        await qs.adelete()

        logger.info(f"Running cleanup after clearing data type {data_type} in dataset {dataset_id} via API")
        n_removed = await run_all_cleanup()
        logger.info(f"Cleanup: removed {n_removed} objects in total")

        return Response(status=status.HTTP_204_NO_CONTENT)

    # Otherwise: GET

    authz_middleware.mark_authz_done(request)
    return Response(await make_data_type_response_object(
        data_type,
        dt.DATA_TYPES[data_type],
        project=str(project.identifier),
        dataset=dataset_id,
        include_counts=(await can_see_counts(request, resource)),
    ))


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def dataset_data_type_summary(request: HttpRequest, dataset_id: str):
    dataset = await Dataset.objects.aget(identifier=dataset_id)
    project = await Project.objects.aget(datasets=dataset)

    base_resource = create_resource(project, dataset, None)
    has_permission: bool = await can_see_counts(request, dataset, base_resource)

    dt_response = []
    for dt_id, dt_d in dt.DATA_TYPES.items():
        try:
            has_dt_permission: bool = has_permission or (
                await can_see_counts(request, create_resource(project, dataset, dt_id)))
            dt_response.append(
                await make_data_type_response_object(
                    dt_id,
                    dt_d,
                    project.identifier,
                    dataset.identifier,
                    include_counts=has_dt_permission,
                )
            )
        except ValueError as e:
            return Response(errors.bad_request_error(str(e)), status=status.HTTP_400_BAD_REQUEST)

    dt_response.sort(key=lambda d: d["id"])
    return Response(dt_response)
