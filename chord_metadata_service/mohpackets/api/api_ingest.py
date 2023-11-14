import logging

from django.db import transaction
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


@router.post("/program/")
def create_program(request, payload: ProgramModelSchema):
    program = Program.objects.create(**payload.dict())
    return {"identifier": str(program)}


@router.post("/donor/")
def create_donor(request, payload: DonorIngestSchema):
    donor = Donor.objects.create(**payload.dict())
    return {"identifier": str(donor)}


@router.post("/biomarker/")
def create_biomarker(request, payload: BiomarkerIngestSchema):
    biomarker = Biomarker.objects.create(**payload.dict())
    return {"identifier": str(biomarker)}


@router.post("/chemotherapy/")
def create_chemotherapy(request, payload: ChemotherapyIngestSchema):
    chemotherapy = Chemotherapy.objects.create(**payload.dict())
    return {"identifier": str(chemotherapy)}


@router.post("/comorbidity/")
def create_comorbidity(request, payload: ComorbidityIngestSchema):
    comorbidity = Comorbidity.objects.create(**payload.dict())
    return {"identifier": str(comorbidity)}


@router.post("/exposure/")
def create_exposure(request, payload: ExposureIngestSchema):
    exposure = Exposure.objects.create(**payload.dict())
    return {"identifier": str(exposure)}


@router.post("/followup/")
def create_followup(request, payload: FollowUpIngestSchema):
    followup = FollowUp.objects.create(**payload.dict())
    return {"identifier": str(followup)}


@router.post("/hormonetherapy/")
def create_hormonetherapy(request, payload: HormoneTherapyIngestSchema):
    hormonetherapy = HormoneTherapy.objects.create(**payload.dict())
    return {"identifier": str(hormonetherapy)}


@router.post("/immunotherapy/")
def create_immunotherapy(request, payload: ImmunotherapyIngestSchema):
    immunotherapy = Immunotherapy.objects.create(**payload.dict())
    return {"identifier": str(immunotherapy)}


@router.post("/primarydiagnosis/")
def create_primarydiagnosis(request, payload: PrimaryDiagnosisIngestSchema):
    primarydiagnosis = PrimaryDiagnosis.objects.create(**payload.dict())
    return {"identifier": str(primarydiagnosis)}


@router.post("/radiation/")
def create_radiation(request, payload: RadiationIngestSchema):
    radiation = Radiation.objects.create(**payload.dict())
    return {"identifier": str(radiation)}


@router.post("/sampleregistration/")
def create_sampleregistration(request, payload: SampleRegistrationIngestSchema):
    sampleregistration = SampleRegistration.objects.create(**payload.dict())
    return {"identifier": str(sampleregistration)}


@router.post("/specimen/")
def create_specimen(request, payload: SpecimenIngestSchema):
    specimen = Specimen.objects.create(**payload.dict())
    return {"identifier": str(specimen)}


@router.post("/surgery/")
def create_surgery(request, payload: SurgeryIngestSchema):
    surgery = Surgery.objects.create(**payload.dict())
    return {"identifier": str(surgery)}


@router.post("/treatment/")
def create_treatment(request, payload: TreatmentIngestSchema):
    treatment = Treatment.objects.create(**payload.dict())
    return {"identifier": str(treatment)}
