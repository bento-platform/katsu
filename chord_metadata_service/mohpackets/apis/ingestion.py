from http import HTTPStatus
from typing import Type

from django.http import HttpResponse, JsonResponse
from ninja import Router

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
from chord_metadata_service.mohpackets.schemas.ingestion import (
    BiomarkerIngestSchema,
    ChemotherapyIngestSchema,
    ComorbidityIngestSchema,
    DonorIngestSchema,
    ExposureIngestSchema,
    FollowUpIngestSchema,
    HormoneTherapyIngestSchema,
    ImmunotherapyIngestSchema,
    PrimaryDiagnosisIngestSchema,
    RadiationIngestSchema,
    SampleRegistrationIngestSchema,
    SpecimenIngestSchema,
    SurgeryIngestSchema,
    TreatmentIngestSchema,
)
from chord_metadata_service.mohpackets.schemas.model import ProgramModelSchema

"""
Module with create APIs for clinical data.
These APIs require admin authorization

Author: Son Chau
"""

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


@router.post("/follow_up/")
def create_follow_up(request, payload: FollowUpIngestSchema, response: HttpResponse):
    return create_instance(payload, FollowUp)


@router.post("/hormone_therapy/")
def create_hormone_therapy(
    request, payload: HormoneTherapyIngestSchema, response: HttpResponse
):
    return create_instance(payload, HormoneTherapy)


@router.post("/immunotherapy/")
def create_immunotherapy(
    request, payload: ImmunotherapyIngestSchema, response: HttpResponse
):
    return create_instance(payload, Immunotherapy)


@router.post("/primary_diagnosis/")
def create_primary_diagnosis(
    request, payload: PrimaryDiagnosisIngestSchema, response: HttpResponse
):
    return create_instance(payload, PrimaryDiagnosis)


@router.post("/radiation/")
def create_radiation(request, payload: RadiationIngestSchema, response: HttpResponse):
    return create_instance(payload, Radiation)


@router.post("/sample_registration/")
def create_sample_registration(
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
