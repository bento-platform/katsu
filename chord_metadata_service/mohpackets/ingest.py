import json
import time
from typing import List

from django.db import transaction
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from chord_metadata_service.mohpackets.models import Program
from chord_metadata_service.mohpackets.serializers import ProgramSerializer


@extend_schema(
    description="data ngest",
    responses={
        200: inline_serializer(
            name="data_ingest",
            fields={
                "ingest": serializers.IntegerField(),
            },
        )
    },
)
@api_view(["GET"])
def ingest_data(_request):
    try:
        with open(
            "./chord_metadata_service/mohpackets/data/synthetic_data/progz.json", "r"
        ) as f:
            programs_json = f.read()
    except FileNotFoundError as e:
        return Response(status=status.HTTP_404_NOT_FOUND, data={"error": str(e)})
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": str(e)})

    try:
        start_time = time.process_time()
        create_bulk_programs(programs_json)
        end_time = time.process_time()
        print("Time taken: ", end_time - start_time)
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": str(e)})

    return Response(status=status.HTTP_201_CREATED)


def create_bulk_programs(programs: str):
    """Create a list of programs in bulk.

    Parameters
    ----------
    programs : str
        JSON string representing a list of programs to be created.

    Raises
    ------
    ValueError
        If the input is not a valid JSON string.
    ValidationError
        If the input data is not valid according to the serializer.
    """
    # Parse the JSON string into a list of dictionaries
    try:
        programs_data = json.loads(programs)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format.")

    # Use the serializer to validate and create the programs
    serializer = ProgramSerializer(data=programs_data, many=True)
    serializer.is_valid(raise_exception=True)
    with transaction.atomic():
        # serializer.save()
        program_objs = [Program(**item) for item in programs_data]
        Program.objects.bulk_create(program_objs)
