from functools import wraps
from http import HTTPStatus
from typing import Dict, List

from django.db.models import Prefetch, Q
from ninja import Query

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
from chord_metadata_service.mohpackets.pagination import (
    CustomRouterPaginated,
)
from chord_metadata_service.mohpackets.schemas.filter import (
    BiomarkerFilterSchema,
    ChemotherapyFilterSchema,
    ComorbidityFilterSchema,
    DonorFilterSchema,
    ExposureFilterSchema,
    FollowUpFilterSchema,
    HormoneTherapyFilterSchema,
    ImmunotherapyFilterSchema,
    PrimaryDiagnosisFilterSchema,
    ProgramFilterSchema,
    RadiationFilterSchema,
    SampleRegistrationFilterSchema,
    SpecimenFilterSchema,
    SurgeryFilterSchema,
    TreatmentFilterSchema,
)
from chord_metadata_service.mohpackets.schemas.model import (
    BiomarkerModelSchema,
    ChemotherapyModelSchema,
    ComorbidityModelSchema,
    DonorModelSchema,
    ExposureModelSchema,
    FollowUpModelSchema,
    HormoneTherapyModelSchema,
    ImmunotherapyModelSchema,
    PrimaryDiagnosisModelSchema,
    ProgramModelSchema,
    RadiationModelSchema,
    SampleRegistrationModelSchema,
    SpecimenModelSchema,
    SurgeryModelSchema,
    TreatmentModelSchema,
)
from chord_metadata_service.mohpackets.schemas.nested_data import (
    DonorWithClinicalDataSchema,
)

"""
Module with authorized APIs for patient clinical data.
These APIs require authorization and only returns the objects related
to the datasets that user authorized to see.

Author: Son Chau
"""


router = CustomRouterPaginated()


##########################################
#                                        #
#           HELPER FUNCTIONS             #
#                                        #
##########################################
def require_donor_by_program(func):
    @wraps(func)
    def wrapper(request, filters):
        if filters.submitter_donor_id and not filters.program_id:
            error_message = {"error": "filter missing program_id"}
            return HTTPStatus.BAD_REQUEST, error_message

        return func(request, filters)

    return wrapper


##########################################
#                                        #
#           DELETE FUNCTIONS             #
#                                        #
##########################################
@router.delete(
    "/program/{program_id}/",
    response={204: None, 404: Dict[str, str]},
)
def delete_program(request, program_id: str):
    try:
        dataset = Program.objects.get(pk=program_id)
        dataset.delete()
        return HTTPStatus.NO_CONTENT, None
    except Program.DoesNotExist:
        return HTTPStatus.NOT_FOUND, {"error": "Program matching query does not exist"}


##########################################
#                                        #
#        DONOR WITH CLINICAL DATA        #
#                                        #
##########################################
@router.get(
    "/donor_with_clinical_data/program/{program_id}/donor/{donor_id}",
    response={200: DonorWithClinicalDataSchema, 404: Dict[str, str]},
)
def get_donor_with_clinical_data(request, program_id: str, donor_id: str):
    authorized_datasets = request.authorized_datasets
    q = (
        Q(program_id__in=authorized_datasets)
        & Q(program_id=program_id)
        & Q(submitter_donor_id=donor_id)
    )
    queryset = Donor.objects.filter(q)

    donor_followups_prefetch = Prefetch(
        "followup_set",
        queryset=FollowUp.objects.filter(
            submitter_primary_diagnosis_id__isnull=True,
            submitter_treatment_id__isnull=True,
        ),
    )

    primary_diagnosis_followups_prefetch = Prefetch(
        "primarydiagnosis_set__followup_set",
        queryset=FollowUp.objects.filter(
            submitter_primary_diagnosis_id__isnull=False,
            submitter_treatment_id__isnull=True,
        ),
    )
    try:
        donor = queryset.prefetch_related(
            donor_followups_prefetch,
            primary_diagnosis_followups_prefetch,
            "biomarker_set",
            "comorbidity_set",
            "exposure_set",
            "primarydiagnosis_set__treatment_set__chemotherapy_set",
            "primarydiagnosis_set__treatment_set__hormonetherapy_set",
            "primarydiagnosis_set__treatment_set__immunotherapy_set",
            "primarydiagnosis_set__treatment_set__radiation_set",
            "primarydiagnosis_set__treatment_set__surgery_set",
            "primarydiagnosis_set__treatment_set__followup_set",
            "primarydiagnosis_set__specimen_set__sampleregistration_set",
        ).get()
        return donor
    except Donor.DoesNotExist:
        return HTTPStatus.NOT_FOUND, {
            "error": "Donor matching query does not exist or inaccessible"
        }


##########################################
#                                        #
#             CLINICAL DATA              #
#                                        #
##########################################
@router.get(
    "/programs/",
    response=List[ProgramModelSchema],
)
def list_programs(request, filters: Query[ProgramFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Program.objects.filter(q)


@router.get("/donors/", response=List[DonorModelSchema])
def list_donors(request, filters: Query[DonorFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Donor.objects.filter(q)


def check_filter_donor_with_program(filters):
    if filters.submitter_donor_id and not filters.program_id:
        error_message = {"error": "submitter_donor_id filter requires program_id"}
        return HTTPStatus.BAD_REQUEST, error_message
    return filters


@router.get(
    "/primary_diagnoses/",
    response=List[PrimaryDiagnosisModelSchema],
)
def list_primary_diagnoses(request, filters: Query[PrimaryDiagnosisFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return PrimaryDiagnosis.objects.filter(q)


@router.get(
    "/biomarkers/",
    response=List[BiomarkerModelSchema],
)
def list_biomarkers(request, filters: Query[BiomarkerFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Biomarker.objects.filter(q)


@router.get(
    "/chemotherapies/",
    response=List[ChemotherapyModelSchema],
)
def list_chemotherapies(request, filters: Query[ChemotherapyFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Chemotherapy.objects.filter(q)


@router.get(
    "/comorbidities/",
    response=List[ComorbidityModelSchema],
)
def list_comorbidities(request, filters: Query[ComorbidityFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Comorbidity.objects.filter(q)


@router.get(
    "/exposures/",
    response=List[ExposureModelSchema],
)
def list_exposures(request, filters: Query[ExposureFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Exposure.objects.filter(q)


@router.get(
    "/follow_ups/",
    response=List[FollowUpModelSchema],
)
def list_follow_ups(request, filters: Query[FollowUpFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return FollowUp.objects.filter(q)


@router.get(
    "/hormone_therapies/",
    response=List[HormoneTherapyModelSchema],
)
def list_hormone_therapies(request, filters: Query[HormoneTherapyFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return HormoneTherapy.objects.filter(q)


@router.get(
    "/immunotherapies/",
    response=List[ImmunotherapyModelSchema],
)
def list_immunotherapies(request, filters: Query[ImmunotherapyFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Immunotherapy.objects.filter(q)


@router.get(
    "/radiations/",
    response=List[RadiationModelSchema],
)
def list_radiations(request, filters: Query[RadiationFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Radiation.objects.filter(q)


@router.get(
    "/sample_registrations/",
    response=List[SampleRegistrationModelSchema],
)
def list_sample_registrations(request, filters: Query[SampleRegistrationFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return SampleRegistration.objects.filter(q)


@router.get(
    "/specimens/",
    response=List[SpecimenModelSchema],
)
def list_specimens(request, filters: Query[SpecimenFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Specimen.objects.filter(q)


@router.get(
    "/surgeries/",
    response=List[SurgeryModelSchema],
)
def list_surgeries(request, filters: Query[SurgeryFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Surgery.objects.filter(q)


@router.get(
    "/treatments/",
    response=List[TreatmentModelSchema],
)
def list_treatments(request, filters: Query[TreatmentFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Treatment.objects.filter(q)
