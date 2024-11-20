from typing import List

from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import (
    Case,
    CharField,
    Func,
    IntegerField,
    OuterRef,
    Q,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import Abs, Cast
from ninja import Query, Router

from chord_metadata_service.mohpackets.models import (
    Donor,
    Treatment,
)
from chord_metadata_service.mohpackets.schemas.explorer import (
    DonorExplorerSchema,
)
from chord_metadata_service.mohpackets.schemas.filter import (
    DonorExplorerFilterSchema,
)

"""
Module with explorer APIs for statistic.
These APIs requires a service token and bypass user authorization.

Author: Son Chau
"""

explorer_router = Router()


@explorer_router.get("/donors/", response=List[DonorExplorerSchema])
def explorer_donor(request, filters: DonorExplorerFilterSchema = Query(...)):
    """
    Returns a list of donors with their sample IDs, treatment types, age, and primary site.
    This endpoint is called by the query service and bypasses user authorization.
    """
    filter_dict = filters.dict()
    queryset = (
        Donor.objects.select_related("program_id")
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
        abs_month_interval=Abs(
            Cast("date_of_birth__month_interval", output_field=IntegerField())
        ),
        age_at_diagnosis=Case(
            When(Q(date_of_birth__isnull=True), then=Value(None)),
            When(abs_month_interval__lt=240, then=Value("0-19")),
            When(abs_month_interval__lt=360, then=Value("20-29")),
            When(abs_month_interval__lt=480, then=Value("30-39")),
            When(abs_month_interval__lt=600, then=Value("40-49")),
            When(abs_month_interval__lt=720, then=Value("50-59")),
            When(abs_month_interval__lt=840, then=Value("60-69")),
            When(abs_month_interval__lt=960, then=Value("70-79")),
            default=Value("80+"),
            output_field=CharField(),
        ),
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
    ).values(
        "program_id",
        "submitter_donor_id",
        "submitter_sample_ids",
        "primary_site",
        "treatment_type",
        "age_at_diagnosis",
    )
    return donors
