import logging

from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from chord_metadata_service.mohpackets.permissions import CanDIGAdminOrReadOnly
from chord_metadata_service.mohpackets.serializers import (
    BiomarkerSerializer,
    ChemotherapySerializer,
    ComorbiditySerializer,
    DonorSerializer,
    ExposureSerializer,
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
    The function has some decorators:
    - @extend_schema: document the API endpoint using OpenAPI.
    - @api_view: specify the HTTP methods that the endpoint accepts.
    - @permission_classes: specify the permissions required to access the endpoint.
"""

##########################################
#                                        #
#           HELPER FUNCTIONS             #
#                                        #
##########################################

logger = logging.getLogger(__name__)


def create_bulk_objects(serializer_class, data: dict):
    """Create a list of objects in bulk using a list of JSON strings.

    This function uses the provided serializer class to validate the input data before
    creating the objects in bulk using the provided model.

    Parameters
    ----------
    data : dict
        A JSON object representing the objects to be created.
    serializer_class: class
        The serializer class used to validate the input data before creating the objects.
    """

    # Use the serializer to validate the input data
    serializer = serializer_class(data=data, many=True)
    serializer.is_valid(raise_exception=True)
    # Note: bulk_create() would be faster but it requires to append the _id to the foreign keys
    with transaction.atomic():
        serializer.save()
    objs = serializer.data
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
@permission_classes([CanDIGAdminOrReadOnly])
def ingest_programs(request):
    serializer = ProgramSerializer
    data = request.data
    try:
        objs = create_bulk_objects(serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={"result": len(objs)},
    )


# DONOR
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
@permission_classes([CanDIGAdminOrReadOnly])
def ingest_donors(request):
    serializer = DonorSerializer
    data = request.data
    try:
        objs = create_bulk_objects(serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={"result": len(objs)},
    )


# PRIMARY DIAGNOSIS
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
@permission_classes([CanDIGAdminOrReadOnly])
def ingest_primary_diagnosises(request):
    serializer = PrimaryDiagnosisSerializer
    data = request.data
    try:
        objs = create_bulk_objects(serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={"result": len(objs)},
    )


# SPECIMEN
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
@permission_classes([CanDIGAdminOrReadOnly])
def ingest_specimens(request):
    serializer = SpecimenSerializer
    data = request.data
    try:
        objs = create_bulk_objects(serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={"result": len(objs)},
    )


# SAMPLE REGISTRATION
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
@permission_classes([CanDIGAdminOrReadOnly])
def ingest_sample_registrations(request):
    serializer = SampleRegistrationSerializer
    data = request.data
    try:
        objs = create_bulk_objects(serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={"result": len(objs)},
    )


# TREATMENT
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
@permission_classes([CanDIGAdminOrReadOnly])
def ingest_treatments(request):
    serializer = TreatmentSerializer
    data = request.data
    try:
        objs = create_bulk_objects(serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={"result": len(objs)},
    )


# CHEMOTHERAPY
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
@permission_classes([CanDIGAdminOrReadOnly])
def ingest_chemotherapies(request):
    serializer = ChemotherapySerializer
    data = request.data
    try:
        objs = create_bulk_objects(serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={"result": len(objs)},
    )


# RADIATION
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
@permission_classes([CanDIGAdminOrReadOnly])
def ingest_radiations(request):
    serializer = RadiationSerializer
    data = request.data
    try:
        objs = create_bulk_objects(serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={"result": len(objs)},
    )


# SURGERY
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
@permission_classes([CanDIGAdminOrReadOnly])
def ingest_surgeries(request):
    serializer = SurgerySerializer
    data = request.data
    try:
        objs = create_bulk_objects(serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={"result": len(objs)},
    )


# HORMONE THERAPY
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
@permission_classes([CanDIGAdminOrReadOnly])
def ingest_hormonetherapies(request):
    serializer = HormoneTherapySerializer
    data = request.data
    try:
        objs = create_bulk_objects(serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={"result": len(objs)},
    )


# IMMUNOTHERAPY
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
@permission_classes([CanDIGAdminOrReadOnly])
def ingest_immunotherapies(request):
    serializer = ImmunotherapySerializer
    data = request.data
    try:
        objs = create_bulk_objects(serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={"result": len(objs)},
    )


# FOLLOW UP
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
@permission_classes([CanDIGAdminOrReadOnly])
def ingest_followups(request):
    serializer = FollowUpSerializer
    data = request.data
    try:
        objs = create_bulk_objects(serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={"result": len(objs)},
    )


# BIOMARKER
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
@permission_classes([CanDIGAdminOrReadOnly])
def ingest_biomarkers(request):
    serializer = BiomarkerSerializer
    data = request.data
    try:
        objs = create_bulk_objects(serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={"result": len(objs)},
    )


# COMORBIDITY
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
@permission_classes([CanDIGAdminOrReadOnly])
def ingest_comorbidities(request):
    serializer = ComorbiditySerializer
    data = request.data
    try:
        objs = create_bulk_objects(serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={"result": len(objs)},
    )


# EXPOSURE
# ---------------
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
@permission_classes([CanDIGAdminOrReadOnly])
def ingest_exposures(request):
    serializer = ExposureSerializer
    data = request.data
    try:
        objs = create_bulk_objects(serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={"result": len(objs)},
    )
