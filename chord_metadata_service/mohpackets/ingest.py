import json
import time
from typing import List

from django.apps import apps
from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from chord_metadata_service.mohpackets.models import (
    Biomarker,
    Chemotherapy,
    Comorbidity,
    Donor,
    FollowUp,
    HormoneTherapy,
    Immunotherapy,
    PrimaryDiagnosis,
    Program,
    Radiation,
    SampleRegistration,
    Specimen,
    Surgery,
    Treatment,
)
from chord_metadata_service.mohpackets.serializers import (
    BiomarkerSerializer,
    ChemotherapySerializer,
    ComorbiditySerializer,
    DonorSerializer,
    FollowUpSerializer,
    HormoneTherapySerializer,
    ImmunotherapySerializer,
    IngestRequestSerializer,
    PrimaryDiagnosisSerializer,
    ProgramSerializer,
    RadiationSerializer,
    SampleRegistrationSerializer,
    SpecimenSerializer,
    SurgerySerializer,
    TreatmentSerializer,
)

"""
    This module contains the API endpoints for ingesting bulk data into the database.
    It take a JSON object with a "data" key and a list of JSON objects as the value.
    It then uses the serializer class to validate the input data before creating the objects in bulk.  
"""

##########################################
#                                        #
#           HELPER FUNCTIONS             #
#                                        #
##########################################


def create_bulk_objects(model, serializer_class, data: dict):
    """Create a list of objects in bulk using a list of JSON strings.

    This function uses the provided serializer class to validate the input data before
    creating the objects in bulk using the provided model.

    Parameters
    ----------
    model : class
        The model class for the objects to be created.
    data : dict
        A JSON object representing the objects to be created.
    serializer_class: class
        The serializer class used to validate the input data before creating the objects.
    """

    if "data" not in data:
        raise ValueError("Invalid data format. Expected a JSON object with 'data' key.")
    data_list = data["data"]

    # Use the serializer to validate the input data
    serializer = serializer_class(data=data_list, many=True)
    serializer.is_valid(raise_exception=True)

    # Create the objects in bulk
    with transaction.atomic():
        objects = [model(**item) for item in data_list]
        objs = model.objects.bulk_create(objects)

    return objs


##########################################
#                                        #
#         BULK INGEST FUNCTIONS          #
#                                        #
##########################################

# PROGRAM
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
def ingest_programs(request):
    model = Program
    serializer = ProgramSerializer
    data = request.data
    try:
        objs = create_bulk_objects(model, serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error during ingest_programs": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"Ingestion Successful! {len(objs)} programs were created."},
    )


# DONOR
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
def ingest_donors(request):
    model = Donor
    serializer = DonorSerializer
    data = request.data
    try:
        objs = create_bulk_objects(model, serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error during ingest_donors": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"Ingestion Successful! {len(objs)} donors were created."},
    )


# PRIMARY DIAGNOSIS
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
def ingest_primary_diagnosises(request):
    model = PrimaryDiagnosis
    serializer = PrimaryDiagnosisSerializer
    data = request.data
    try:
        objs = create_bulk_objects(model, serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error during ingest_primary_diagnosises": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"Ingestion Successful! {len(objs)} primary diagnosises were created."},
    )


# SPECIMEN
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
def ingest_specimens(request):
    model = Specimen
    serializer = SpecimenSerializer
    data = request.data
    try:
        objs = create_bulk_objects(model, serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error during ingest_specimens": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"Ingestion Successful! {len(objs)} specimens were created."},
    )


# SAMPLE REGISTRATION
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
def ingest_sample_registrations(request):
    model = SampleRegistration
    serializer = SampleRegistrationSerializer
    data = request.data
    try:
        objs = create_bulk_objects(model, serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error during ingest_sample_registrations": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"Ingestion Successful! {len(objs)} sample registrations were created."},
    )


# TREATMENT
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
def ingest_treatments(request):
    model = Treatment
    serializer = TreatmentSerializer
    data = request.data
    try:
        objs = create_bulk_objects(model, serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error during ingest_treatments": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"Ingestion Successful! {len(objs)} treatments were created."},
    )


# CHEMOTHERAPY
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
def ingest_chemotherapies(request):
    model = Chemotherapy
    serializer = ChemotherapySerializer
    data = request.data
    try:
        objs = create_bulk_objects(model, serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error during ingest_chemotherapies": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"Ingestion Successful! {len(objs)} chemotherapies were created."},
    )


# RADIATION
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
def ingest_radiations(request):
    model = Radiation
    serializer = RadiationSerializer
    data = request.data
    try:
        objs = create_bulk_objects(model, serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error during ingest_radiations": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"Ingestion Successful! {len(objs)} radiations were created."},
    )


# SURGERY
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
def ingest_surgeries(request):
    model = Surgery
    serializer = SurgerySerializer
    data = request.data
    try:
        objs = create_bulk_objects(model, serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error during ingest_surgeries": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"Ingestion Successful! {len(objs)} surgeries were created."},
    )


# HORMONE THERAPY
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
def ingest_hormonetherapies(request):
    model = HormoneTherapy
    serializer = HormoneTherapySerializer
    data = request.data
    try:
        objs = create_bulk_objects(model, serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error during ingest_hormonetherapies": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"Ingestion Successful! {len(objs)} hormonetherapies were created."},
    )


# IMMUNOTHERAPY
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
def ingest_immunotherapies(request):
    model = Immunotherapy
    serializer = ImmunotherapySerializer
    data = request.data
    try:
        objs = create_bulk_objects(model, serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error during ingest_immunotherapies": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"Ingestion Successful! {len(objs)} immunotherapies were created."},
    )


# FOLLOW UP
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
def ingest_followups(request):
    model = FollowUp
    serializer = FollowUpSerializer
    data = request.data
    try:
        objs = create_bulk_objects(model, serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error during ingest_followups": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"Ingestion Successful! {len(objs)} followups were created."},
    )


# BIOMARKER
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
def ingest_biomarkers(request):
    model = Biomarker
    serializer = BiomarkerSerializer
    data = request.data
    try:
        objs = create_bulk_objects(model, serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error during ingest_biomarkers": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"Ingestion Successful! {len(objs)} biomarkers were created."},
    )


# COMORBIDITY
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
def ingest_comorbidities(request):
    model = Comorbidity
    serializer = ComorbiditySerializer
    data = request.data
    try:
        objs = create_bulk_objects(model, serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error during ingest_comorbidities": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"Ingestion Successful! {len(objs)} comorbidities were created."},
    )
