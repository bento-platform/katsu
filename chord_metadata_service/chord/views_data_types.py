from bento_lib.responses import errors
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpRequest

from adrf.decorators import api_view
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from typing import Callable, Dict, Optional
from chord_metadata_service.chord.models import Dataset, Project
from chord_metadata_service.chord.permissions import OverrideOrSuperUserOnly, ReadOnly
from chord_metadata_service.mcode.models import MCodePacket

from chord_metadata_service.phenopackets.models import Phenopacket
from chord_metadata_service.experiments.models import Experiment, ExperimentResult

from . import data_types as dt

QUERYSET_FN: Dict[str, Callable] = {
    dt.DATA_TYPE_EXPERIMENT: lambda dataset_id: Experiment.objects.filter(dataset_id=dataset_id),
    dt.DATA_TYPE_MCODEPACKET: lambda dataset_id: MCodePacket.objects.filter(dataset_id=dataset_id),
    dt.DATA_TYPE_PHENOPACKET: lambda dataset_id: Phenopacket.objects.filter(dataset_id=dataset_id),
}


async def get_count_for_data_type(
    data_type: str,
    project: Optional[str] = None,
    dataset: Optional[str] = None,
) -> Optional[int]:
    """
    Returns the count for a particular data type. If dataset is provided, project will be ignored. If neither are
    provided, the count will be for the whole node.
    """

    if data_type == dt.DATA_TYPE_READSET:
        # No counts for readset, it's a fake data type inside Katsu...
        return None

    q: Optional[QuerySet] = None

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
    project: Optional[str],
    dataset: Optional[str],
) -> dict:
    return {
        **data_type_details,
        "id": data_type_id,
        "count": await get_count_for_data_type(data_type_id, project, dataset),
    }


@api_view(["GET"])
@permission_classes([AllowAny])
async def data_type_list(request: HttpRequest):
    # TODO: Permissions: only return counts when we are authenticated/have access to counts or full data.

    project = request.GET.get("project", "").strip() or None
    dataset = request.GET.get("dataset", "").strip() or None

    dt_response = []
    for dt_id, dt_d in dt.DATA_TYPES.items():
        try:
            dt_response.append(await make_data_type_response_object(dt_id, dt_d, project, dataset))
        except ValueError as e:
            return Response(errors.bad_request_error(str(e)), status=status.HTTP_400_BAD_REQUEST)

    dt_response.sort(key=lambda d: d["id"])
    return Response(dt_response)


@api_view(["GET"])
@permission_classes([AllowAny])
async def data_type_detail(request: HttpRequest, data_type: str):
    # TODO: Permissions: only return counts when we are authenticated/have access to counts or full data.

    if data_type not in dt.DATA_TYPES:
        return Response(errors.not_found_error(f"Data type {data_type} not found"), status=status.HTTP_404_NOT_FOUND)

    project = request.GET.get("project", "").strip() or None
    dataset = request.GET.get("dataset", "").strip() or None

    try:
        return Response(await make_data_type_response_object(data_type, dt.DATA_TYPES[data_type], project, dataset))
    except ValueError as e:
        return Response(errors.bad_request_error(str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([AllowAny])
async def data_type_schema(_request: HttpRequest, data_type: str):
    # TODO: exclude extra_properties schema
    if data_type not in dt.DATA_TYPES:
        return Response(errors.not_found_error(f"Data type {data_type} not found"), status=status.HTTP_404_NOT_FOUND)

    return Response(dt.DATA_TYPES[data_type]["schema"])


@api_view(["GET"])
@permission_classes([AllowAny])
async def data_type_metadata_schema(_request: HttpRequest, data_type: str):
    if data_type not in dt.DATA_TYPES:
        return Response(errors.not_found_error(f"Data type {data_type} not found"), status=status.HTTP_404_NOT_FOUND)

    return Response(dt.DATA_TYPES[data_type]["metadata_schema"])


@api_view(["GET", "DELETE"])
@permission_classes([OverrideOrSuperUserOnly | ReadOnly])
async def dataset_data_type(request: HttpRequest, dataset_id: str, data_type: str):
    if data_type not in QUERYSET_FN:
        return Response(errors.bad_request_error, status=status.HTTP_400_BAD_REQUEST)
    qs = QUERYSET_FN[data_type](dataset_id)

    if request.method == "DELETE":
        await qs.adelete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    project = await Project.objects.aget(datasets=dataset_id)
    response_object = await make_data_type_response_object(data_type, dt.DATA_TYPES[data_type],
                                                           project=str(project.identifier), dataset=dataset_id)

    return Response(response_object)


@api_view(["GET"])
@permission_classes([OverrideOrSuperUserOnly | ReadOnly])
async def dataset_summary(request: HttpRequest, dataset_id: str):
    dataset = await Dataset.objects.aget(identifier=dataset_id)
    project = await Project.objects.aget(datasets=dataset)

    dt_response = []
    for dt_id, dt_d in dt.DATA_TYPES.items():
        try:
            dt_response.append(
                await make_data_type_response_object(dt_id, dt_d, project.identifier, dataset.identifier)
            )
        except ValueError as e:
            return Response(errors.bad_request_error(str(e)), status=status.HTTP_400_BAD_REQUEST)

    dt_response.sort(key=lambda d: d["id"])
    return Response(dt_response)
