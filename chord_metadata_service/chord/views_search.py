import itertools

from chord_lib.responses.errors import *
from chord_lib.search import build_search_response, postgres
from datetime import datetime
from django.db import connection
from psycopg2 import sql
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Dataset
from .permissions import OverrideOrSuperUserOnly
from chord_metadata_service.metadata.settings import DEBUG
from chord_metadata_service.phenopackets.models import Phenopacket
from chord_metadata_service.phenopackets.schemas import PHENOPACKET_SCHEMA
from chord_metadata_service.phenopackets.serializers import PhenopacketSerializer

PHENOPACKET_DATA_TYPE_ID = "phenopacket"

PHENOPACKET_METADATA_SCHEMA = {
    "type": "object"
    # TODO
}


@api_view(["GET"])
@permission_classes([AllowAny])
def data_type_list(_request):
    return Response([{"id": PHENOPACKET_DATA_TYPE_ID, "schema": PHENOPACKET_SCHEMA}])


@api_view(["GET"])
@permission_classes([AllowAny])
def data_type_phenopacket(_request):
    return Response({
        "id": PHENOPACKET_DATA_TYPE_ID,
        "schema": PHENOPACKET_SCHEMA,
        "metadata_schema": PHENOPACKET_METADATA_SCHEMA
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def data_type_phenopacket_schema(_request):
    return Response(PHENOPACKET_SCHEMA)


@api_view(["GET"])
@permission_classes([AllowAny])
def data_type_phenopacket_metadata_schema(_request):
    return Response(PHENOPACKET_METADATA_SCHEMA)


@api_view(["GET"])
@permission_classes([AllowAny])
def table_list(request):
    data_types = request.query_params.getlist("data-type")
    if PHENOPACKET_DATA_TYPE_ID not in data_types:
        return Response(bad_request_error(f"Missing or invalid data type (Specified: {data_types})"), status=400)

    return Response([{
        "id": d.identifier,
        "name": d.title,
        "metadata": {
            "description": d.description,
            "project_id": d.project_id,
            "created": d.created.isoformat(),
            "updated": d.updated.isoformat()
        },
        "schema": PHENOPACKET_SCHEMA
    } for d in Dataset.objects.all()])


# TODO: Remove pragma: no cover when GET/POST implemented
# TODO: Should this exist? managed
@api_view(["DELETE"])
@permission_classes([OverrideOrSuperUserOnly])
def table_detail(request, table_id):  # pragma: no cover
    # TODO: Implement GET, POST
    # TODO: Permissions: Check if user has control / more direct access over this dataset? Or just always use owner...
    try:
        table = Dataset.objects.get(identifier=table_id)
    except Dataset.DoesNotExist:
        return Response(not_found_error(f"Table with ID {table_id} not found"), status=404)

    if request.method == "DELETE":
        table.delete()
        return Response(status=204)


def phenopacket_results(query, params, key="id"):
    with connection.cursor() as cursor:
        if DEBUG:
            print(f"[CHORD Metadata {datetime.now()}] [DEBUG] Executing SQL:\n    {query.as_string(cursor.connection)}",
                  flush=True)
        cursor.execute(query.as_string(cursor.connection), params)
        return set(dict(zip([col[0] for col in cursor.description], row))[key] for row in cursor.fetchall())


def phenopacket_query_results(query, params):
    return Phenopacket.objects.filter(id__in=phenopacket_results(query, params, "id"))


def search(request, internal_data=False):
    if "data_type" not in request.data:
        return Response(bad_request_error("Missing data_type in request body"), status=400)

    if "query" not in request.data:
        return Response(bad_request_error("Missing query in request body"), status=400)

    start = datetime.now()

    if request.data["data_type"] != PHENOPACKET_DATA_TYPE_ID:
        return Response(bad_request_error(f"Missing or invalid data type (Specified: {request.data['data_type']})"),
                        status=400)

    try:
        compiled_query, params = postgres.search_query_to_psycopg2_sql(request.data["query"], PHENOPACKET_SCHEMA)
    except (SyntaxError, TypeError, ValueError) as e:
        return Response(bad_request_error(f"Error compiling query (message: {str(e)})"), status=400)

    if not internal_data:
        datasets = Dataset.objects.filter(identifier__in=phenopacket_results(
            query=compiled_query,
            params=params,
            key="dataset_id"
        ))  # TODO: Maybe can avoid hitting DB here
        return Response(build_search_response([{"id": d.identifier, "data_type": PHENOPACKET_DATA_TYPE_ID}
                                               for d in datasets], start))

    return Response(build_search_response({
        dataset_id: {
            "data_type": PHENOPACKET_DATA_TYPE_ID,
            "matches": list(PhenopacketSerializer(p).data for p in dataset_phenopackets)
        } for dataset_id, dataset_phenopackets in itertools.groupby(
            phenopacket_query_results(compiled_query, params),
            key=lambda p: str(p.dataset_id)
        )
    }, start))


@api_view(["POST"])
@permission_classes([AllowAny])
def chord_search(request):
    return search(request, internal_data=False)


@api_view(["POST"])
@permission_classes([AllowAny])
def chord_private_search(request):
    # Private search endpoints are protected by URL namespace, not by Django permissions.
    return search(request, internal_data=True)


@api_view(["POST"])
def chord_private_table_search(request, table_id):  # Search phenopacket data types in specific tables
    # Private search endpoints are protected by URL namespace, not by Django permissions.
    start = datetime.now()

    if DEBUG:
        print(f"[CHORD Metadata {datetime.now()}] [DEBUG] Started private table search", flush=True)

    if request.data is None or "query" not in request.data:
        # TODO: Better error
        return Response(bad_request_error("Missing query in request body"), status=400)

    # Check that dataset exists
    dataset = Dataset.objects.get(identifier=table_id)

    try:
        compiled_query, params = postgres.search_query_to_psycopg2_sql(request.data["query"], PHENOPACKET_SCHEMA)
    except (SyntaxError, TypeError, ValueError) as e:
        print("[CHORD Metadata] Error encountered compiling query {}:\n    {}".format(request.data["query"], str(e)))
        return Response(bad_request_error(f"Error compiling query (message: {str(e)})"), status=400)

    if DEBUG:
        print(f"[CHORD Metadata {datetime.now()}] [DEBUG] Finished compiling query in {datetime.now() - start}",
              flush=True)

    query_results = phenopacket_query_results(
        query=sql.SQL("{} AND dataset_id = {}").format(compiled_query, sql.Placeholder()),
        params=params + (dataset.identifier,)
    )

    if DEBUG:
        print(f"[CHORD Metadata {datetime.now()}] [DEBUG] Finished running query in {datetime.now() - start}",
              flush=True)

    serialized_data = PhenopacketSerializer(query_results, many=True).data

    if DEBUG:
        print(f"[CHORD Metadata {datetime.now()}] [DEBUG] Finished running query and serializing in "
              f"{datetime.now() - start}", flush=True)

    return Response(build_search_response(serialized_data, start))
