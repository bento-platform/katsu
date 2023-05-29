import logging
import os
from datetime import datetime

from django.core.management import CommandError, call_command
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from chord_metadata_service.mohpackets.permissions import CanDIGAdminOrReadOnly, CustodianOrAdminOnly
from chord_metadata_service.mohpackets.serializers import (
    BiomarkerSerializer,
    ChemotherapySerializer,
    ComorbiditySerializer,
    DonorSerializer,
    ExposureSerializer,
    FollowUpSerializer,
    HormoneTherapySerializer,
    ImmunotherapySerializer,
    PrimaryDiagnosisSerializer,
    ProgramSerializer,
    RadiationSerializer,
    SampleRegistrationSerializer,
    SpecimenSerializer,
    SurgerySerializer,
    TreatmentSerializer,
)
from chord_metadata_service.mohpackets.throttling import MoHRateThrottle

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

class IngestMixin:
    """
        This mixin should be used for viewsets that are used for ingesting dataa.

        The authentication classes are set based on the `DJANGO_SETTINGS_MODULE`.
        If the env is "dev" or "prod", the `TokenAuthentication` class is
        used. Otherwise, the `LocalAuthentication` class is used.

        Methods
        -------
        ingest_data()
            Returns a filtered queryset that includes only the objects that the user is
            authorized to see based on their permissions.
        """
    serializer = None
    ingest_name = "Unknown"
    def create(self, request):
        serializer = self.serializer
        name = self.ingest_name
        data = request.data
        try:
            if not data:
                raise ValueError("Ingest request body is empty.")
            objs = create_bulk_objects(serializer, data)
        except Exception as e:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"error during ingest_%s" % name: str(e)},
            )

        return Response(
            status=status.HTTP_201_CREATED,
            data={f"{len(objs)} %s were created." % name},
        )


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
        objs = serializer.save()

    return objs


def backup_db():
    """Backup the database with current date and time."""
    backup_db_folder = "chord_metadata_service/mohpackets/data/backup_db"
    os.makedirs(backup_db_folder, exist_ok=True)
    db_name = f"db_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    try:
        call_command("dumpdata", output=f"{backup_db_folder}/{db_name}")
    except Exception as e:
        logger.error(f"Error during backup_db: {e}")
        raise CommandError("Error during backup_db") from e


##########################################
#                                        #
#         BULK INGEST FUNCTIONS          #
#                                        #
##########################################

# PROGRAM
# ---------------
'''
@extend_schema(
    request=IngestRequestSerializer,
    responses={201: OpenApiTypes.STR},
)
@api_view(["POST"])
@permission_classes([CustodianOrAdminOnly])

def ingest_programs(request):
    serializer = ProgramSerializer
    data = request.data
    try:
        objs = create_bulk_objects(serializer, data)
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error during ingest_programs": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"{len(objs)} programs were created."},
    )
'''
class IngestProgramViewSet(IngestMixin, viewsets.GenericViewSet):
    ingest_name = "Programs"
    serializer = ProgramSerializer
    permission_classes = [CustodianOrAdminOnly]
    throttle_classes = [MoHRateThrottle]

# DONOR
# ---------------
class IngestDonorViewSet(IngestMixin, viewsets.GenericViewSet):
    ingest_name = "Donors"
    serializer = DonorSerializer
    permission_classes = [CustodianOrAdminOnly]
    throttle_classes = [MoHRateThrottle]

# PRIMARY DIAGNOSIS
# ---------------
class IngestPrimaryDiagnosisViewSet(IngestMixin, viewsets.GenericViewSet):
    ingest_name = "Primary Diagnoses"
    serializer = PrimaryDiagnosisSerializer
    permission_classes = [CustodianOrAdminOnly]
    throttle_classes = [MoHRateThrottle]

# SPECIMEN
# ---------------
class IngestSpecimenViewSet(IngestMixin, viewsets.GenericViewSet):
    ingest_name = "Specimen"
    serializer = SpecimenSerializer
    permission_classes = [CustodianOrAdminOnly]
    throttle_classes = [MoHRateThrottle]


# SAMPLE REGISTRATION
# ---------------
class IngestSampleRegistrationViewSet(IngestMixin, viewsets.GenericViewSet):
    ingest_name = "Sample Registrations"
    serializer = SampleRegistrationSerializer
    permission_classes = [CustodianOrAdminOnly]
    throttle_classes = [MoHRateThrottle]


# TREATMENT
# ---------------
class IngestTreatmentViewSet(IngestMixin, viewsets.GenericViewSet):
    ingest_name = "Treatments"
    serializer = TreatmentSerializer
    permission_classes = [CustodianOrAdminOnly]
    throttle_classes = [MoHRateThrottle]

# CHEMOTHERAPY
# ---------------
class IngestChemotherapyViewSet(IngestMixin, viewsets.GenericViewSet):
    ingest_name = "Chemotherapies"
    serializer = ChemotherapySerializer
    permission_classes = [CustodianOrAdminOnly]
    throttle_classes = [MoHRateThrottle]

# RADIATION
# ---------------
class IngestRadiationViewSet(IngestMixin, viewsets.GenericViewSet):
    ingest_name = "Radiations"
    serializer = RadiationSerializer
    permission_classes = [CustodianOrAdminOnly]
    throttle_classes = [MoHRateThrottle]

# SURGERY
# ---------------
class IngestSurgeryViewSet(IngestMixin, viewsets.GenericViewSet):
    ingest_name = "Surgeries"
    serializer = SurgerySerializer
    permission_classes = [CustodianOrAdminOnly]
    throttle_classes = [MoHRateThrottle]


# HORMONE THERAPY
# ---------------
class IngestHormoneTherapyViewSet(IngestMixin, viewsets.GenericViewSet):
    ingest_name = "Hormone Therapies"
    serializer = HormoneTherapySerializer
    permission_classes = [CustodianOrAdminOnly]
    throttle_classes = [MoHRateThrottle]

# IMMUNOTHERAPY
# ---------------
class IngestImmunotherapyViewSet(IngestMixin, viewsets.GenericViewSet):
    ingest_name = "Immunotherapies"
    serializer = ImmunotherapySerializer
    permission_classes = [CustodianOrAdminOnly]
    throttle_classes = [MoHRateThrottle]


# FOLLOW UP
# ---------------
class IngestFollowUpViewSet(IngestMixin, viewsets.GenericViewSet):
    ingest_name = "Followups"
    serializer = FollowUpSerializer
    permission_classes = [CustodianOrAdminOnly]
    throttle_classes = [MoHRateThrottle]

# BIOMARKER
# ---------------
class IngestBiomarkerViewSet(IngestMixin, viewsets.GenericViewSet):
    ingest_name = "Biomarkers"
    serializer = BiomarkerSerializer
    permission_classes = [CustodianOrAdminOnly]
    throttle_classes = [MoHRateThrottle]

# COMORBIDITY
# ---------------
class IngestComorbidityViewSet(IngestMixin, viewsets.GenericViewSet):
    ingest_name = "Comorbidities"
    serializer = ComorbiditySerializer
    permission_classes = [CustodianOrAdminOnly]
    throttle_classes = [MoHRateThrottle]

# EXPOSURE
# ---------------
class IngestExposureViewSet(IngestMixin, viewsets.GenericViewSet):
    ingest_name = "Exposures"
    serializer = ExposureSerializer
    permission_classes = [CustodianOrAdminOnly]
    throttle_classes = [MoHRateThrottle]

@extend_schema(
    responses={204: OpenApiTypes.STR},
)
@api_view(["DELETE"])
@permission_classes([CanDIGAdminOrReadOnly])
def delete_all(request):
    """
    Clean all the tables in the database
    """
    try:
        backup_db()
        call_command("flush", interactive=False, verbosity=0)
    except Exception as e:
        return HttpResponse(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return HttpResponse(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    responses={200: OpenApiTypes.STR},
)
@api_view(["GET"])
@permission_classes([CanDIGAdminOrReadOnly])
def version_check(_request):
    return JsonResponse({"version": "2.0.0"}, status=status.HTTP_200_OK)