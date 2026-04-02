from http import HTTPStatus

from django.http import JsonResponse
from django.db.models import Q
from ninja import Router

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
from chord_metadata_service.mohpackets.schemas.download import (
    DownloadResponseSchema,
    SummaryMessageSchema,
)
from chord_metadata_service.mohpackets.schemas.filter import DownloadFilterSchema

router = Router()


@router.post("/clinical_data/", response=DownloadResponseSchema)
def search_clinical_data(request, filters: DownloadFilterSchema):
    """
    Filters clinical data based on criteria provided in the POST request
    body. Returns record counts and optionally the detailed data based
    on the 'summary_only' flag.
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
                return JsonResponse(
                    error_message,
                    status=HTTPStatus.BAD_REQUEST,
                )

        if program_ids and sample_ids:
            filtered_donors_qs = filtered_donors_qs.filter(
                program_id__program_id__in=program_ids,
                sampleregistration__submitter_sample_id__in=sample_ids,
            )
        else:
            filtered_donors_qs = filtered_donors_qs.none()

    filtered_donor_uuids = list(filtered_donors_qs.values_list("uuid", flat=True))
    donor_count = len(filtered_donor_uuids)

    # 2. --- Get QuerySets and Counts for Related Models ---
    models_to_query = {
        "donors": Donor,
        "primary_diagnoses": PrimaryDiagnosis,
        "specimens": Specimen,
        "sample_registrations": SampleRegistration,
        "treatments": Treatment,
        "systemic_therapies": SystemicTherapy,
        "radiations": Radiation,
        "surgeries": Surgery,
        "follow_ups": FollowUp,
        "biomarkers": Biomarker,
        "comorbidities": Comorbidity,
        "exposures": Exposure,
    }

    querysets_to_download = {}
    record_counts = {}

    if not filtered_donor_uuids:
        # If no donors match, all counts are 0
        for name in models_to_query:
            record_counts[name] = 0
        message = "No matching records found for the given criteria."
    else:
        for name, model in models_to_query.items():
            filter_kwargs = {}
            if name == "donors":
                filter_kwargs["uuid__in"] = filtered_donor_uuids
            else:
                filter_kwargs["donor_uuid__in"] = filtered_donor_uuids

            qs = model.objects.filter(**filter_kwargs)
            record_counts[name] = qs.count()
            # Only store the full queryset if detailed data is requested
            if not filters.summary_only:
                querysets_to_download[name] = qs
        message = f"Found {donor_count} matching donors."

    # 3. --- Construct Response ---
    summary_payload = SummaryMessageSchema(message=message, record_counts=record_counts)

    response_payload = {"summary": summary_payload}

    if not filters.summary_only and donor_count > 0:
        response_payload["data"] = querysets_to_download
    elif not filters.summary_only and donor_count == 0:
        response_payload["data"] = None

    return response_payload
