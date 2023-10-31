import os
from typing import List, Optional

import orjson
from authx.auth import get_opa_datasets
from django.conf import settings
from django.db.models import Prefetch, Q
from ninja import Field, FilterSchema, ModelSchema, NinjaAPI, Query, Schema
from ninja.orm import create_schema
from ninja.pagination import PageNumberPagination, paginate
from ninja.parser import Parser
from ninja.renderers import BaseRenderer
from ninja.security import HttpBearer

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
from chord_metadata_service.mohpackets.schema import (
    DonorSchema,
    DonorWithClinicalDataSchema,
)
from chord_metadata_service.mohpackets.utils import LocalAuthentication, has_permission


# =========================================================
class ORJSONRenderer(BaseRenderer):
    media_type = "application/json"

    def render(self, request, data, *, response_status):
        return orjson.dumps(data)


class ORJSONParser(Parser):
    def parse_body(self, request):
        return orjson.loads(request.body)


settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
# Use jwt token auth in prod/dev environment
if "dev" in settings_module or "prod" in settings_module:
    auth = TokenAuthentication
else:
    auth = LocalAuthentication


api = NinjaAPI(renderer=ORJSONRenderer(), parser=ORJSONParser(), auth=auth)
# api = NinjaAPI()
# ===============================================================


@api.get("/ninja_donors", response=List[DonorWithClinicalDataSchema])
@paginate(PageNumberPagination, page_size=10)
def tasks(request):
    # queryset = Donor.objects.all()

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
    queryset = Donor.objects.prefetch_related(
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
    ).all()
    return list(queryset)


class DonorFilterSchema(FilterSchema):
    submitter_donor_id: Optional[str] = None
    gender: Optional[str] = Field(None, q="gender__icontains")


@api.get("/donors/", response=List[DonorSchema], auth=LocalAuthentication())
def list_donors(request, filters: DonorFilterSchema = Query(...)):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Donor.objects.filter(q)
