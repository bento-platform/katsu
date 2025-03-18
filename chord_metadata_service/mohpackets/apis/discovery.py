from typing import Any, Dict, List

from django.conf import settings
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import (
    Case,
    CharField,
    Count,
    F,
    Func,
    IntegerField,
    OuterRef,
    Q,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import Abs, Cast, Coalesce
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from ninja import Query, Router
from ninja.decorators import decorate_view

from chord_metadata_service.mohpackets.models import (
    Donor,
    PrimaryDiagnosis,
    Program,
    SystemicTherapy,
    Treatment,
)
from chord_metadata_service.mohpackets.permissible_values import (
    PRIMARY_SITE,
    TREATMENT_TYPE,
)
from chord_metadata_service.mohpackets.schemas.discovery import (
    DiagnosisAgeCountSchema,
    GenderCountSchema,
    PatientPerProgramSchema,
    PrimarySiteCountSchema,
    ProgramDiscoverySchema,
    TreatmentTypeCountSchema,
)
from chord_metadata_service.mohpackets.schemas.explorer import (
    DonorExplorerSchema,
)
from chord_metadata_service.mohpackets.schemas.filter import (
    DonorExplorerFilterSchema,
)

"""
Module with overview APIs for the summary page and discovery APIs.
Required query service token.
It also masks the value if the data is too small.

Author: Son Chau
"""
CACHE_DURATION = settings.CACHE_DURATION
discovery_router = Router()
overview_router = Router()
explorer_router = Router()
discovery_router.add_router("/overview/", overview_router, tags=["overview"])

# To protect privacy, numbers below a certain threshold will be censored, e.g., <5
SMALL_NUMBER_THRESHOLD = int(settings.AGGREGATE_COUNT_THRESHOLD)
SMALL_NUMBER_DISPLAY = "<" + str(SMALL_NUMBER_THRESHOLD)


###############################################
#                                             #
#               DISCOVERY API                 #
#                                             #
###############################################


@discovery_router.get("/programs/", response=List[ProgramDiscoverySchema])
@decorate_view(cache_page(CACHE_DURATION))
@decorate_view(vary_on_headers("X-Service-Token"))
def discover_programs(request):
    """
    Return all the programs in the database.
    """
    return Program.objects.only("program_id", "metadata")


@discovery_router.get("/sidebar_list/", response=Dict[str, Any])
@decorate_view(cache_page(CACHE_DURATION))
@decorate_view(vary_on_headers("X-Service-Token"))
def discover_sidebar_list(request):
    """
    Retrieve the list of drug names and treatment for frontend usage
    """
    # Drugs queryable for systemic therapy
    systemic_therapy_drug_names = list(
        SystemicTherapy.objects.exclude(drug_name__isnull=True)
        .values_list("drug_name", flat=True)
        .order_by("drug_name")
        .distinct()
    )

    result = {
        "treatment_types": TREATMENT_TYPE,
        "tumour_primary_sites": PRIMARY_SITE,
        "drug_names": systemic_therapy_drug_names,
    }

    return result


###############################################
#                                             #
#                OVERVIEW API                 #
#                                             #
###############################################


@overview_router.get("/program_count/", response=Dict[str, int])
@decorate_view(cache_page(CACHE_DURATION))
@decorate_view(vary_on_headers("X-Service-Token"))
def discover_program_count(request):
    """
    Return the number of programs in the database.
    """
    return {"program_count": Program.objects.count()}


@overview_router.get("/patients_per_program/", response=List[PatientPerProgramSchema])
@decorate_view(cache_page(CACHE_DURATION))
@decorate_view(vary_on_headers("X-Service-Token"))
def discover_patients_per_program(request):
    """
    Return the number of patients per program in the database.
    """
    result = (
        Donor.objects.values("program_id")
        .annotate(count=Count("uuid"))
        .annotate(
            patients_count=Case(
                When(
                    count__lt=SMALL_NUMBER_THRESHOLD,
                    then=Value(SMALL_NUMBER_DISPLAY),
                ),
                default=Cast(F("count"), output_field=CharField()),
            )
        )
        .values("program_id", "patients_count")
    )
    return result


@overview_router.get("/individual_count/", response=Dict[str, str])
@decorate_view(cache_page(CACHE_DURATION))
@decorate_view(vary_on_headers("X-Service-Token"))
def discover_individual_count(request):
    """
    Return the number of individuals in the database.
    """
    donor_count = Donor.objects.count()

    if donor_count == 0:
        result = "0"
    elif donor_count < SMALL_NUMBER_THRESHOLD:
        result = SMALL_NUMBER_DISPLAY
    else:
        result = str(donor_count)

    return {"individual_count": result}


@overview_router.get("/gender_count/", response=List[GenderCountSchema])
@decorate_view(cache_page(CACHE_DURATION))
@decorate_view(vary_on_headers("X-Service-Token"))
def discover_gender_count(request):
    """
    Return the count for every gender in the database.
    """
    result = (
        Donor.objects.values("gender")
        .annotate(count=Count("uuid"))
        .annotate(
            gender_count=Case(
                When(
                    count__lt=SMALL_NUMBER_THRESHOLD,
                    then=Value(SMALL_NUMBER_DISPLAY),
                ),
                default=Cast(F("count"), output_field=CharField()),
            )
        )
        .values("gender", "gender_count")
    )
    return result


@overview_router.get("/primary_site_count/", response=List[PrimarySiteCountSchema])
@decorate_view(cache_page(CACHE_DURATION))
@decorate_view(vary_on_headers("X-Service-Token"))
def discover_primary_site_count(request):
    """
    Return the count for every cancer type in the database.
    """
    result = (
        PrimaryDiagnosis.objects.values("primary_site")
        .annotate(count=Count("uuid"))
        .annotate(
            primary_site_count=Case(
                When(
                    count__lt=SMALL_NUMBER_THRESHOLD,
                    then=Value(SMALL_NUMBER_DISPLAY),
                ),
                default=Cast(F("count"), output_field=CharField()),
            )
        )
        .annotate(primary_site_name=F("primary_site"))
        .values("primary_site_name", "primary_site_count")
    )
    return result


@overview_router.get("/treatment_type_count/", response=List[TreatmentTypeCountSchema])
@decorate_view(cache_page(CACHE_DURATION))
@decorate_view(vary_on_headers("X-Service-Token"))
def discover_treatment_type_count(request):
    """
    Return the count for every treatment type in the database.
    """

    result = (
        Treatment.objects.annotate(
            treatment_type_name=Func(
                Coalesce(F("treatment_type"), Value(["None"])), function="unnest"
            )
        )
        .values("treatment_type_name")
        .annotate(count=Count("uuid"))
        .annotate(
            treatment_type_count=Case(
                When(
                    count__lt=SMALL_NUMBER_THRESHOLD,
                    then=Value(SMALL_NUMBER_DISPLAY),
                ),
                default=Cast(F("count"), output_field=CharField()),
            )
        )
        .values("treatment_type_name", "treatment_type_count")
    )

    return result


@overview_router.get("/diagnosis_age_count/", response=List[DiagnosisAgeCountSchema])
@decorate_view(cache_page(CACHE_DURATION))
@decorate_view(vary_on_headers("X-Service-Token"))
def discover_diagnosis_age_count(request):
    """
    Return the count for age of diagnosis by calculating the date of birth interval.
    """
    result = (
        Donor.objects.annotate(
            abs_month_interval=Abs(
                Cast("date_of_birth__month_interval", output_field=IntegerField())
            ),
            age_at_diagnosis=Case(
                When(Q(date_of_birth__isnull=True), then=Value("null")),
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
        )
        .values(
            "age_at_diagnosis",
        )
        .annotate(count=Count("uuid"))
        .annotate(
            age_count=Case(
                When(
                    count__lt=SMALL_NUMBER_THRESHOLD,
                    then=Value(SMALL_NUMBER_DISPLAY),
                ),
                default=Cast("count", output_field=CharField()),
            )
        )
        .values("age_at_diagnosis", "age_count")
    )

    return result


###############################################
#                                             #
#                EXPLORER API                 #
#                                             #
###############################################


@explorer_router.get("/donors/", response=List[DonorExplorerSchema])
@decorate_view(cache_page(CACHE_DURATION))
@decorate_view(vary_on_headers("X-Service-Token"))
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
