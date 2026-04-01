from functools import wraps
from http import HTTPStatus
from typing import Dict, List

from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import (
    Func,
    OuterRef,
    Prefetch,
    Q,
    Subquery,
)
from ninja import Query
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
from chord_metadata_service.mohpackets.pagination import (
    CustomRouterPaginated,
)
from chord_metadata_service.mohpackets.schemas.filter import (
    BiomarkerFilterSchema,
    ComorbidityFilterSchema,
    DonorExplorerFilterSchema,
    DonorFilterSchema,
    ExposureFilterSchema,
    FollowUpFilterSchema,
    PrimaryDiagnosisFilterSchema,
    ProgramFilterSchema,
    RadiationFilterSchema,
    SampleRegistrationFilterSchema,
    SpecimenFilterSchema,
    SurgeryFilterSchema,
    SystemicTherapyFilterSchema,
    TreatmentFilterSchema,
)
from chord_metadata_service.mohpackets.schemas.model import (
    BiomarkerModelSchema,
    ComorbidityModelSchema,
    DonorModelSchema,
    ExposureModelSchema,
    FollowUpModelSchema,
    PrimaryDiagnosisModelSchema,
    ProgramModelSchema,
    QueryDonorSchema,
    RadiationModelSchema,
    SampleRegistrationModelSchema,
    SpecimenModelSchema,
    SurgeryModelSchema,
    SystemicTherapyModelSchema,
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
    """
    Decorator that make sure `submitter_donor_id` filters must have a corresponding
    `program_id`. Returns an error if `program_id` is missing, preventing filtering
    by `submitter_donor_id` alone.
    """

    @wraps(func)
    def wrapper(request, filters):
        if filters.submitter_donor_id and not filters.program_id:
            error_message = {"error": "filter missing program_id"}
            return Status(HTTPStatus.BAD_REQUEST, error_message)

        return func(request, filters)

    return wrapper


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
    """
    Retrieves a single donor along with all related clinical data, organized in a nested JSON format.
    """
    q = (
        Q(program_id__in=request.read_datasets)
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
            "primarydiagnosis_set__treatment_set__systemictherapy_set",
            "primarydiagnosis_set__treatment_set__radiation_set",
            "primarydiagnosis_set__treatment_set__surgery_set",
            "primarydiagnosis_set__treatment_set__followup_set",
            "primarydiagnosis_set__specimen_set__sampleregistration_set",
        ).get()
        return donor
    except Donor.DoesNotExist:
        return Status(
            HTTPStatus.NOT_FOUND,
            {"error": "Donor matching query does not exist or inaccessible"},
        )


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
    q = Q(program_id__in=request.read_datasets)
    q &= filters.get_filter_expression()
    return Program.objects.filter(q)


@router.get("/donors/", response=List[DonorModelSchema])
def list_donors(request, filters: Query[DonorFilterSchema]):
    q = Q(program_id__in=request.read_datasets)
    q &= filters.get_filter_expression()
    return Donor.objects.filter(q)


@router.get("/query/", response=List[QueryDonorSchema])
def query_donors(request, filters: DonorExplorerFilterSchema = Query(...)):
    """
    Used by the query service to return donors along with their sample IDs, treatment types, and primary sites.
    """
    filter_dict = filters.dict()
    queryset = (
        Donor.objects.filter(Q(program_id__in=request.read_datasets))
        .select_related("program_id")
        .prefetch_related(
            "treatment_set",
            "primarydiagnosis_set",
            "systemictherapy_set",
            "sampleregistration_set",
        )
        .distinct()
    )

    if filter_dict["primary_site"]:
        queryset = queryset.filter(
            primarydiagnosis__primary_site__in=filter_dict["primary_site"]
        )

    if filter_dict["treatment_type"]:
        queryset = queryset.filter(
            treatment__treatment_type__overlap=filter_dict["treatment_type"]
        )

    if filter_dict["systemic_therapy_drug_name"]:
        queryset = queryset.filter(
            systemictherapy__drug_name__in=filter_dict["systemic_therapy_drug_name"]
        )

    if filter_dict["exclude_programs"]:
        queryset = queryset.exclude(program_id__in=filter_dict["exclude_programs"])

    class Unnest(Func):
        contains_subquery = True
        function = "unnest"

    # treatment can have duplicates for counting purpose
    treatment_type_names = (
        Treatment.objects.filter(donor_uuid_id=OuterRef("uuid"))
        .annotate(treatment_type_list=Unnest("treatment_type"))
        .values_list("treatment_type_list", flat=True)
    )

    donors = queryset.annotate(
        submitter_sample_ids=ArrayAgg(
            "sampleregistration__submitter_sample_id",
            distinct=True,
            filter=~Q(sampleregistration__submitter_sample_id=None),
        ),
        primary_site=ArrayAgg(
            "primarydiagnosis__primary_site",
            distinct=True,
            filter=~Q(primarydiagnosis__primary_site=None),
        ),
        treatment_type=ArraySubquery(Subquery(treatment_type_names)),
    )
    return donors


def check_filter_donor_with_program(filters):
    if filters.submitter_donor_id and not filters.program_id:
        error_message = {"error": "submitter_donor_id filter requires program_id"}
        return Status(HTTPStatus.BAD_REQUEST, error_message)
    return filters


@router.get(
    "/primary_diagnoses/",
    response=List[PrimaryDiagnosisModelSchema],
)
def list_primary_diagnoses(request, filters: Query[PrimaryDiagnosisFilterSchema]):
    q = Q(program_id__in=request.read_datasets)
    q &= filters.get_filter_expression()
    return PrimaryDiagnosis.objects.filter(q)


@router.get(
    "/biomarkers/",
    response=List[BiomarkerModelSchema],
)
def list_biomarkers(request, filters: Query[BiomarkerFilterSchema]):
    q = Q(program_id__in=request.read_datasets)
    q &= filters.get_filter_expression()
    return Biomarker.objects.filter(q)


@router.get(
    "/systemic_therapies/",
    response=List[SystemicTherapyModelSchema],
)
def list_systemic_therapies(request, filters: Query[SystemicTherapyFilterSchema]):
    q = Q(program_id__in=request.read_datasets)
    q &= filters.get_filter_expression()
    return SystemicTherapy.objects.filter(q)


@router.get(
    "/comorbidities/",
    response=List[ComorbidityModelSchema],
)
def list_comorbidities(request, filters: Query[ComorbidityFilterSchema]):
    q = Q(program_id__in=request.read_datasets)
    q &= filters.get_filter_expression()
    return Comorbidity.objects.filter(q)


@router.get(
    "/exposures/",
    response=List[ExposureModelSchema],
)
def list_exposures(request, filters: Query[ExposureFilterSchema]):
    q = Q(program_id__in=request.read_datasets)
    q &= filters.get_filter_expression()
    return Exposure.objects.filter(q)


@router.get(
    "/follow_ups/",
    response=List[FollowUpModelSchema],
)
def list_follow_ups(request, filters: Query[FollowUpFilterSchema]):
    q = Q(program_id__in=request.read_datasets)
    q &= filters.get_filter_expression()
    return FollowUp.objects.filter(q)


@router.get(
    "/radiations/",
    response=List[RadiationModelSchema],
)
def list_radiations(request, filters: Query[RadiationFilterSchema]):
    q = Q(program_id__in=request.read_datasets)
    q &= filters.get_filter_expression()
    return Radiation.objects.filter(q)


@router.get(
    "/sample_registrations/",
    response=List[SampleRegistrationModelSchema],
)
def list_sample_registrations(request, filters: Query[SampleRegistrationFilterSchema]):
    q = Q(program_id__in=request.read_datasets)
    q &= filters.get_filter_expression()
    return SampleRegistration.objects.filter(q)


@router.get(
    "/specimens/",
    response=List[SpecimenModelSchema],
)
def list_specimens(request, filters: Query[SpecimenFilterSchema]):
    q = Q(program_id__in=request.read_datasets)
    q &= filters.get_filter_expression()
    return Specimen.objects.filter(q)


@router.get(
    "/surgeries/",
    response=List[SurgeryModelSchema],
)
def list_surgeries(request, filters: Query[SurgeryFilterSchema]):
    q = Q(program_id__in=request.read_datasets)
    q &= filters.get_filter_expression()
    return Surgery.objects.filter(q)


@router.get(
    "/treatments/",
    response=List[TreatmentModelSchema],
)
def list_treatments(request, filters: Query[TreatmentFilterSchema]):
    q = Q(program_id__in=request.read_datasets)
    q &= filters.get_filter_expression()
    return Treatment.objects.filter(q)
