from bento_lib.responses import errors

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .data_types import DATA_TYPE_PHENOPACKET, DATA_TYPES

OUTPUT_FORMAT_VALUES_LIST = "values_list"
OUTPUT_FORMAT_BENTO_SEARCH_RESULT = "bento_search_result"


@api_view(["GET"])
@permission_classes([AllowAny])
def data_type_list(_request):
    return Response(sorted(
        ({"id": k, "label": dt["label"], "schema": dt["schema"]} for k, dt in DATA_TYPES.items()),
        key=lambda dt: dt["id"]
    ))


@api_view(["GET"])
@permission_classes([AllowAny])
def data_type_detail(_request, data_type: str):
    if data_type not in DATA_TYPES:
        return Response(errors.not_found_error(f"Date type {data_type} not found"), status=404)

    return Response({"id": data_type, **DATA_TYPES[data_type]})


@api_view(["GET"])
@permission_classes([AllowAny])
def data_type_schema(_request, data_type: str):
    if data_type not in DATA_TYPES:
        return Response(errors.not_found_error(f"Date type {data_type} not found"), status=404)

    return Response(DATA_TYPES[data_type]["schema"])


@api_view(["GET"])
@permission_classes([AllowAny])
def data_type_metadata_schema(_request, data_type: str):
    if data_type not in DATA_TYPES:
        return Response(errors.not_found_error(f"Date type {data_type} not found"), status=404)

    return Response(DATA_TYPES[DATA_TYPE_PHENOPACKET]["metadata_schema"])
