import logging
from http import HTTPStatus
from typing import Type

from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from ninja import Field, FilterSchema, ModelSchema, Query, Router, Schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from chord_metadata_service.mohpackets.models import (
    Biomarker,
    Chemotherapy,
    Comorbidity,
    Donor,
    Exposure,
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
from chord_metadata_service.mohpackets.permissions import CanDIGAdminOrReadOnly
from chord_metadata_service.mohpackets.schema.schema import (
    BiomarkerFilterSchema,
    BiomarkerIngestSchema,
    BiomarkerModelSchema,
    ChemotherapyFilterSchema,
    ChemotherapyIngestSchema,
    ChemotherapyModelSchema,
    ComorbidityFilterSchema,
    ComorbidityIngestSchema,
    ComorbidityModelSchema,
    DonorFilterSchema,
    DonorIngestSchema,
    DonorModelSchema,
    DonorWithClinicalDataSchema,
    ExposureFilterSchema,
    ExposureIngestSchema,
    ExposureModelSchema,
    FollowUpFilterSchema,
    FollowUpIngestSchema,
    FollowUpModelSchema,
    HormoneTherapyFilterSchema,
    HormoneTherapyIngestSchema,
    HormoneTherapyModelSchema,
    ImmunotherapyFilterSchema,
    ImmunotherapyIngestSchema,
    ImmunotherapyModelSchema,
    PrimaryDiagnosisFilterSchema,
    PrimaryDiagnosisIngestSchema,
    PrimaryDiagnosisModelSchema,
    ProgramFilterSchema,
    ProgramModelSchema,
    RadiationFilterSchema,
    RadiationIngestSchema,
    RadiationModelSchema,
    SampleRegistrationFilterSchema,
    SampleRegistrationIngestSchema,
    SampleRegistrationModelSchema,
    SpecimenFilterSchema,
    SpecimenIngestSchema,
    SpecimenModelSchema,
    SurgeryFilterSchema,
    SurgeryIngestSchema,
    SurgeryModelSchema,
    TreatmentFilterSchema,
    TreatmentIngestSchema,
    TreatmentModelSchema,
)
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
        objs = serializer.save()

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
            data={"error during ingest_programs": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"{len(objs)} programs were created."},
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
            data={"error during ingest_donors": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"{len(objs)} donors were created."},
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
            data={"error during ingest_primary_diagnosises": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"{len(objs)} primary diagnosises were created."},
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
            data={"error during ingest_specimens": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"{len(objs)} specimens were created."},
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
            data={"error during ingest_sample_registrations": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"{len(objs)} sample registrations were created."},
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
            data={"error during ingest_treatments": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"{len(objs)} treatments were created."},
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
            data={"error during ingest_chemotherapies": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"{len(objs)} chemotherapies were created."},
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
            data={"error during ingest_radiations": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"{len(objs)} radiations were created."},
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
            data={"error during ingest_surgeries": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"{len(objs)} surgeries were created."},
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
            data={"error during ingest_hormonetherapies": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"{len(objs)} hormonetherapies were created."},
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
            data={"error during ingest_immunotherapies": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"{len(objs)} immunotherapies were created."},
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
            data={"error during ingest_followups": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"{len(objs)} followups were created."},
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
            data={"error during ingest_biomarkers": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"{len(objs)} biomarkers were created."},
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
            data={"error during ingest_comorbidities": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"{len(objs)} comorbidities were created."},
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
            data={"error during exposures": str(e)},
        )

    return Response(
        status=status.HTTP_201_CREATED,
        data={f"{len(objs)} exposures were created."},
    )


# ===============================================================================
router = Router()


def create_instance(payload, model_cls: Type):
    try:
        instance = model_cls.objects.create(**payload.dict())
    except Exception as e:
        return JsonResponse(
            status=HTTPStatus.BAD_REQUEST,
            data={"detail": str(e)},
        )
    return JsonResponse(
        status=HTTPStatus.CREATED,
        data={"created": str(instance)},
    )


@router.post("/program/")
def create_program(request, payload: ProgramModelSchema, response: HttpResponse):
    return create_instance(payload, Program)


@router.post("/donor/")
def create_donor(request, payload: DonorIngestSchema, response: HttpResponse):
    return create_instance(payload, Donor)


@router.post("/biomarker/")
def create_biomarker(request, payload: BiomarkerIngestSchema, response: HttpResponse):
    return create_instance(payload, Biomarker)


@router.post("/chemotherapy/")
def create_chemotherapy(
    request, payload: ChemotherapyIngestSchema, response: HttpResponse
):
    return create_instance(payload, Chemotherapy)


@router.post("/comorbidity/")
def create_comorbidity(
    request, payload: ComorbidityIngestSchema, response: HttpResponse
):
    return create_instance(payload, Comorbidity)


@router.post("/exposure/")
def create_exposure(request, payload: ExposureIngestSchema, response: HttpResponse):
    return create_instance(payload, Exposure)


@router.post("/followup/")
def create_followup(request, payload: FollowUpIngestSchema, response: HttpResponse):
    return create_instance(payload, FollowUp)


@router.post("/hormonetherapy/")
def create_hormonetherapy(
    request, payload: HormoneTherapyIngestSchema, response: HttpResponse
):
    return create_instance(payload, HormoneTherapy)


@router.post("/immunotherapy/")
def create_immunotherapy(
    request, payload: ImmunotherapyIngestSchema, response: HttpResponse
):
    return create_instance(payload, Immunotherapy)


@router.post("/primarydiagnosis/")
def create_primarydiagnosis(
    request, payload: PrimaryDiagnosisIngestSchema, response: HttpResponse
):
    return create_instance(payload, PrimaryDiagnosis)


@router.post("/radiation/")
def create_radiation(request, payload: RadiationIngestSchema, response: HttpResponse):
    return create_instance(payload, Radiation)


@router.post("/sampleregistration/")
def create_sampleregistration(
    request, payload: SampleRegistrationIngestSchema, response: HttpResponse
):
    return create_instance(payload, SampleRegistration)


@router.post("/specimen/")
def create_specimen(request, payload: SpecimenIngestSchema, response: HttpResponse):
    return create_instance(payload, Specimen)


@router.post("/surgery/")
def create_surgery(request, payload: SurgeryIngestSchema, response: HttpResponse):
    return create_instance(payload, Surgery)


@router.post("/treatment/")
def create_treatment(request, payload: TreatmentIngestSchema, response: HttpResponse):
    return create_instance(payload, Treatment)
