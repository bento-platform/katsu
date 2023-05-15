from bento_lib.responses import errors
from django.http import HttpRequest
from django.db.models import QuerySet

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from typing import Optional

from chord_metadata_service.phenopackets.models import Phenopacket
from chord_metadata_service.experiments.models import Experiment, ExperimentResult

from . import data_types as dt

OUTPUT_FORMAT_VALUES_LIST = "values_list"
OUTPUT_FORMAT_BENTO_SEARCH_RESULT = "bento_search_result"


DATA_TYPES_TO_MODEL = {
    dt.DATA_TYPE_PHENOPACKET: Phenopacket
}


def get_count_for_data_type(
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
            q = q.filter(table__ownership_record__dataset_id=dataset)
        elif project:
            q = q.filter(table__ownership_record__dataset__project_id=project)

    elif data_type == dt.DATA_TYPE_EXPERIMENT_RESULT:
        q = ExperimentResult.objects.all()
        if dataset:
            q = q.filter(experiment_set__table__ownership_record__dataset_id=dataset)
        elif project:
            q = q.filter(experiment_set__table__ownership_record__dataset__project_id=project)

    if q is None:
        raise ValueError(f"Unsupported data type for count function: {data_type}")

    return q.count()


@api_view(["GET"])
@permission_classes([AllowAny])
def data_type_list(request: HttpRequest):
    dt_response = []

    for data_type, data_type_details in dt.DATA_TYPES.items():
        dt_response.append({
            "id": data_type,
            "label": data_type_details["label"],
            "schema": data_type_details["schema"],
            "queryable": data_type_details["queryable"],
            "count": get_count_for_data_type(
                data_type,
                request.GET.get("project", "").strip() or None,
                request.GET.get("dataset", "").strip() or None,
            ),
        })

    dt_response.sort(key=lambda d: d["id"])
    return Response(dt_response)


@api_view(["GET"])
@permission_classes([AllowAny])
def data_type_detail(_request: HttpRequest, data_type: str):
    if data_type not in dt.DATA_TYPES:
        return Response(errors.not_found_error(f"Date type {data_type} not found"), status=404)

    return Response({"id": data_type, **dt.DATA_TYPES[data_type]})


@api_view(["GET"])
@permission_classes([AllowAny])
def data_type_schema(_request: HttpRequest, data_type: str):
    if data_type not in dt.DATA_TYPES:
        return Response(errors.not_found_error(f"Date type {data_type} not found"), status=404)

    return Response(dt.DATA_TYPES[data_type]["schema"])


@api_view(["GET"])
@permission_classes([AllowAny])
def data_type_metadata_schema(_request: HttpRequest, data_type: str):
    if data_type not in dt.DATA_TYPES:
        return Response(errors.not_found_error(f"Date type {data_type} not found"), status=404)

    return Response(dt.DATA_TYPES[data_type]["metadata_schema"])
