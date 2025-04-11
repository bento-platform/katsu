from http import HTTPStatus
from typing import List

from django.db.models import Q
from ninja import Field, FilterSchema, Router, Schema
from chord_metadata_service.mohpackets.schemas.model import (
    BiomarkerModelSchema,
    ComorbidityModelSchema,
    DonorModelSchema,
    ExposureModelSchema,
    FollowUpModelSchema,
    PrimaryDiagnosisModelSchema,
    RadiationModelSchema,
    SampleRegistrationModelSchema,
    SpecimenModelSchema,
    SurgeryModelSchema,
    SystemicTherapyModelSchema,
    TreatmentModelSchema,
)
from chord_metadata_service.mohpackets.models import (
    Biomarker,
    Comorbidity,
    Donor,
    Exposure,
    FollowUp,
    PrimaryDiagnosis,
    Radiation,
    SampleRegistration,
    Specimen,
    Surgery,
    SystemicTherapy,
    Treatment,
)

router = Router()


class AllClinicalDataSchema(Schema):
    donors: List[DonorModelSchema]
    primary_diagnoses: List[PrimaryDiagnosisModelSchema]
    specimens: List[SpecimenModelSchema]
    sample_registrations: List[SampleRegistrationModelSchema]
    treatments: List[TreatmentModelSchema]
    systemic_therapies: List[SystemicTherapyModelSchema]
    radiations: List[RadiationModelSchema]
    surgeries: List[SurgeryModelSchema]
    follow_ups: List[FollowUpModelSchema]
    biomarkers: List[BiomarkerModelSchema]
    comorbidities: List[ComorbidityModelSchema]
    exposures: List[ExposureModelSchema]


class DownloadFilterSchema(FilterSchema):
    treatment_type: List[str] = Field(None, q="treatment_type__overlap")
    primary_site: List[str] = Field(None)
    systemic_therapy_drug_name: List[str] = Field(None)
    program_id: List[str] = Field(None)
    biosample_id: List[str] = Field(None)


@router.post("/clinical_data/", response=AllClinicalDataSchema)
def search_clinical_data(request, filters: DownloadFilterSchema):
    """
    Filters clinical data based on criteria provided in the POST request
    body and returns multiple related tables (Donors, PrimaryDiagnoses,
    Specimens, etc.) as a single JSON object
    """
    filter_dict = filters.dict(exclude_none=True)

    # 1. --- Filter Donors ---
    base_donors_qs = (
        Donor.objects.filter(Q(program_id__in=request.download_datasets))
        .select_related("program_id")
        .prefetch_related(
            "treatment_set",
            "primarydiagnosis_set",
            "systemictherapy_set",
            "sampleregistration_set",
        )
        .distinct()
    )

    filtered_donors_qs = base_donors_qs
    if program_id := filter_dict.get("program_id"):
        filtered_donors_qs = filtered_donors_qs.filter(program_id__in=program_id)

    if primary_site := filter_dict.get("primary_site"):
        filtered_donors_qs = filtered_donors_qs.filter(
            primarydiagnosis__primary_site__in=primary_site
        )
    if treatment_type := filter_dict.get("treatment_type"):
        filtered_donors_qs = filtered_donors_qs.filter(
            treatment__treatment_type__overlap=treatment_type
        )
    if drug_name := filter_dict.get("systemic_therapy_drug_name"):
        filtered_donors_qs = filtered_donors_qs.filter(
            systemictherapy__drug_name__in=drug_name
        )

    if biosample_id := filter_dict.get("biosample_id"):
        program_ids = []
        sample_ids = []
        for bio in biosample_id:
            try:
                program_id, sample_id = bio.split("~")
                program_ids.append(program_id)
                sample_ids.append(sample_id)
            except ValueError:
                error_message = {"error": f"Invalid format for biosample_id: {bio}"}
                return router.api.create_response(
                    request, error_message, status=HTTPStatus.BAD_REQUEST
                )

        if program_ids and sample_ids:
            filtered_donors_qs = filtered_donors_qs.filter(
                program_id__program_id__in=program_ids,
                sampleregistration__submitter_sample_id__in=sample_ids,
            )
        else:
            filtered_donors_qs = filtered_donors_qs.none()

    filtered_donor_uuids = list(filtered_donors_qs.values_list("uuid", flat=True))

    if not filtered_donor_uuids:
        return router.api.create_response(
            request,
            {"message": "No matching records found."},
            status=HTTPStatus.OK,
        )

    # 2. --- Get QuerySets for Related Models using the filtered donor UUIDs ---
    querysets_to_download = {
        "donors": Donor.objects.filter(uuid__in=filtered_donor_uuids),
        "primary_diagnoses": PrimaryDiagnosis.objects.filter(
            donor_uuid__in=filtered_donor_uuids
        ),
        "specimens": Specimen.objects.filter(donor_uuid__in=filtered_donor_uuids),
        "sample_registrations": SampleRegistration.objects.filter(
            donor_uuid__in=filtered_donor_uuids
        ),
        "treatments": Treatment.objects.filter(donor_uuid__in=filtered_donor_uuids),
        "systemic_therapies": SystemicTherapy.objects.filter(
            donor_uuid__in=filtered_donor_uuids
        ),
        "radiations": Radiation.objects.filter(donor_uuid__in=filtered_donor_uuids),
        "surgeries": Surgery.objects.filter(donor_uuid__in=filtered_donor_uuids),
        "follow_ups": FollowUp.objects.filter(donor_uuid__in=filtered_donor_uuids),
        "biomarkers": Biomarker.objects.filter(donor_uuid__in=filtered_donor_uuids),
        "comorbidities": Comorbidity.objects.filter(
            donor_uuid__in=filtered_donor_uuids
        ),
        "exposures": Exposure.objects.filter(donor_uuid__in=filtered_donor_uuids),
    }

    return querysets_to_download
