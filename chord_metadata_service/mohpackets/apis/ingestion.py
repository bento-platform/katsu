from http import HTTPStatus
from typing import Dict, List, Type

from django.http import HttpResponse, JsonResponse
from ninja import Router
from ninja.responses import Status

from chord_metadata_service.mohpackets.models import (
    Biomarker,
    Comorbidity,
    Donor,
    Exposure,
    FollowUp,
    PrimaryDiagnosis,
    Program,
    Radiation,
    SampleRegistration,
    Specimen,
    Surgery,
    SystemicTherapy,
    Treatment,
)
from chord_metadata_service.mohpackets.schemas.ingestion import (
    BiomarkerIngestSchema,
    ComorbidityIngestSchema,
    DonorIngestSchema,
    ExposureIngestSchema,
    FollowUpIngestSchema,
    PrimaryDiagnosisIngestSchema,
    ProgramIngestSchema,
    RadiationIngestSchema,
    SampleRegistrationIngestSchema,
    SpecimenIngestSchema,
    SurgeryIngestSchema,
    SystemicTherapyIngestSchema,
    TreatmentIngestSchema,
)

"""
CRUD APIs for clinical data. Require authorization

Author: Son Chau
"""

router = Router()


def create_instances(payload: List, model_cls: Type):
    """
    Create instances of a specified model using data from the provided payload.

    Args:
        payload (List): A list of data objects, where each object contains
                        the data required to create a model instance.
        model_cls (Type): The model class for which instances are to be created.

    Returns:
        JsonResponse: A response with a 201 status and a list of created instances if successful.
                      If an error occurs, it returns a 400 status with an error message.
    """
    instances = []
    try:
        for item in payload:
            instance = model_cls.objects.create(**item.dict())
            instances.append(instance)
    except Exception as e:
        return JsonResponse(
            status=HTTPStatus.BAD_REQUEST,
            data={"error": str(e)},
        )

    created_instances = [str(instance) for instance in instances]
    return JsonResponse(
        status=HTTPStatus.CREATED,
        data={"created": created_instances},
    )


##########################################
#                                        #
#           CREATE FUNCTIONS             #
#                                        #
##########################################


@router.post("/programs/")
def create_programs(
    request, payload: List[ProgramIngestSchema], response: HttpResponse
):
    return create_instances(payload, Program)


@router.post("/donors/")
def create_donors(request, payload: List[DonorIngestSchema], response: HttpResponse):
    return create_instances(payload, Donor)


@router.post("/biomarkers/")
def create_biomarkers(
    request, payload: List[BiomarkerIngestSchema], response: HttpResponse
):
    return create_instances(payload, Biomarker)


@router.post("/systemic_therapies/")
def create_systemic_therapies(
    request, payload: List[SystemicTherapyIngestSchema], response: HttpResponse
):
    return create_instances(payload, SystemicTherapy)


@router.post("/comorbidities/")
def create_comorbidities(
    request, payload: List[ComorbidityIngestSchema], response: HttpResponse
):
    return create_instances(payload, Comorbidity)


@router.post("/exposures/")
def create_exposures(
    request, payload: List[ExposureIngestSchema], response: HttpResponse
):
    return create_instances(payload, Exposure)


@router.post("/followups/")
def create_followups(
    request, payload: List[FollowUpIngestSchema], response: HttpResponse
):
    return create_instances(payload, FollowUp)


@router.post("/primary_diagnoses/")
def create_primary_diagnoses(
    request, payload: List[PrimaryDiagnosisIngestSchema], response: HttpResponse
):
    return create_instances(payload, PrimaryDiagnosis)


@router.post("/radiations/")
def create_radiations(
    request, payload: List[RadiationIngestSchema], response: HttpResponse
):
    return create_instances(payload, Radiation)


@router.post("/sample_registrations/")
def create_sample_registrations(
    request, payload: List[SampleRegistrationIngestSchema], response: HttpResponse
):
    return create_instances(payload, SampleRegistration)


@router.post("/specimens/")
def create_specimens(
    request, payload: List[SpecimenIngestSchema], response: HttpResponse
):
    return create_instances(payload, Specimen)


@router.post("/surgeries/")
def create_surgeries(
    request, payload: List[SurgeryIngestSchema], response: HttpResponse
):
    return create_instances(payload, Surgery)


@router.post("/treatments/")
def create_treatments(
    request, payload: List[TreatmentIngestSchema], response: HttpResponse
):
    return create_instances(payload, Treatment)


##########################################
#                                        #
#           DELETE FUNCTIONS             #
#                                        #
##########################################
delete_router = Router()


@delete_router.delete(
    "/program/{program_id}/",
    response={204: None, 404: Dict[str, str]},
)
def delete_program(request, program_id: str):
    try:
        dataset = Program.objects.get(pk=program_id)
        dataset.delete()
        return Status(HTTPStatus.NO_CONTENT, None)
    except Program.DoesNotExist:
        return Status(
            HTTPStatus.NOT_FOUND,
            {"error": "Program matching query does not exist"},
        )
