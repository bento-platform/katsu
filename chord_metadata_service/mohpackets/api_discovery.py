import os
from collections import Counter, defaultdict
from datetime import date, datetime
from itertools import chain
from typing import Any, Dict, List, Optional, Type

import orjson
from authx.auth import get_opa_datasets
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    CharField,
    Count,
    ExpressionWrapper,
    F,
    FloatField,
    Func,
    Min,
    Model,
    OuterRef,
    Prefetch,
    Q,
    Subquery,
    Value,
)
from django.db.models.functions import Concat
from django.http import HttpResponse, JsonResponse
from drf_spectacular.utils import (
    OpenApiTypes,
    extend_schema,
    extend_schema_serializer,
    inline_serializer,
)
from ninja import Field, FilterSchema, ModelSchema, NinjaAPI, Query, Router, Schema
from ninja.orm import create_schema
from ninja.pagination import PageNumberPagination, paginate
from ninja.parser import Parser
from ninja.renderers import BaseRenderer
from ninja.security import HttpBearer
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response

from chord_metadata_service.mohpackets.api_base import (
    BaseBiomarkerViewSet,
    BaseChemotherapyViewSet,
    BaseComorbidityViewSet,
    BaseDonorViewSet,
    BaseExposureViewSet,
    BaseFollowUpViewSet,
    BaseHormoneTherapyViewSet,
    BaseImmunotherapyViewSet,
    BasePrimaryDiagnosisViewSet,
    BaseRadiationViewSet,
    BaseSampleRegistrationViewSet,
    BaseSpecimenViewSet,
    BaseSurgeryViewSet,
    BaseTreatmentViewSet,
)
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
from chord_metadata_service.mohpackets.permissible_values import (
    PRIMARY_SITE,
    TREATMENT_TYPE,
)
from chord_metadata_service.mohpackets.schema import (
    DiscoverySchema,
    DonorFilterSchema,
    DonorModelSchema,
    ProgramDiscoverySchema,
    SpecimenFilterSchema,
)
from chord_metadata_service.mohpackets.throttling import MoHRateThrottle
from chord_metadata_service.mohpackets.utils import get_schema_url

# from .utils import get_schema_url

"""
    This module inheriting from the base views and adding the discovery mixin,
    which returns the number of donors only.

    The discovery feature can help users without authorization explore the
    available data without exposing the details.
"""


##########################################
#                                        #
#           HELPER FUNCTIONS             #
#                                        #
##########################################


@extend_schema_serializer(many=False)
class DiscoverySerializer(serializers.Serializer):
    """
    This serializer is used to return the discovery_donor.
    It also override the list serializer to a single object
    """

    discovery_donor = serializers.IntegerField()


class DiscoveryMixin:
    """
    This mixin should be used for viewsets that need to expose
    discovery information about the donor they represent.

    Methods
    -------
    list(request, *args, **kwargs)
        Returns a response that contains the number of unique donors in the
        queryset.
    """

    @extend_schema(responses=DiscoverySerializer(many=False))
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        donor_counts = (
            queryset.values("program_id")
            .annotate(count=Count("submitter_donor_id"))
            .order_by("program_id")
        )
        discovery_donor = {
            f"{donor['program_id']}": donor["count"] for donor in donor_counts
        }
        return Response({"discovery_donor": discovery_donor})


def count_terms(terms):
    """
    Return a dictionary of counts for every term in a list, used in overview endpoints
    for fields with lists as entries.
    """
    if len(terms) > 0 and isinstance(terms[0], list):  # Unnest list if nested
        terms = sum(terms, [])
    return Counter(terms)


###############################################
#                                             #
#           DISCOVERY API VIEWS               #
#                                             #
###############################################


class DiscoveryDonorViewSet(DiscoveryMixin, BaseDonorViewSet):
    """
    Retrieves a number of discovery donors.
    """

    pass


class DiscoverySpecimenViewSet(DiscoveryMixin, BaseSpecimenViewSet):
    """
    Retrieves a number of discovery specimens.
    """

    pass


class DiscoverySampleRegistrationViewSet(DiscoveryMixin, BaseSampleRegistrationViewSet):
    """
    Retrieves a number of discovery samples.
    """

    pass


class DiscoveryPrimaryDiagnosisViewSet(DiscoveryMixin, BasePrimaryDiagnosisViewSet):
    """
    Retrieves a number of discovery primary diagnosises.
    """

    pass


class DiscoveryTreatmentViewSet(DiscoveryMixin, BaseTreatmentViewSet):
    """
    Retrieves a number of discovery treatments.
    """

    pass


class DiscoveryChemotherapyViewSet(DiscoveryMixin, BaseChemotherapyViewSet):
    """
    Retrieves a number of discovery chemotherapies.
    """

    pass


class DiscoveryHormoneTherapyViewSet(DiscoveryMixin, BaseHormoneTherapyViewSet):
    """
    Retrieves a number of discovery hormone therapies.
    """

    pass


class DiscoveryRadiationViewSet(DiscoveryMixin, BaseRadiationViewSet):
    """
    Retrieves a number of discovery radiations.
    """

    pass


class DiscoveryImmunotherapyViewSet(DiscoveryMixin, BaseImmunotherapyViewSet):
    """
    Retrieves a number of discovery immuno therapies.
    """

    pass


class DiscoverySurgeryViewSet(DiscoveryMixin, BaseSurgeryViewSet):
    """
    Retrieves a number of discovery surgeries.
    """

    pass


class DiscoveryFollowUpViewSet(DiscoveryMixin, BaseFollowUpViewSet):
    """
    Retrieves a number of discovery follow ups.
    """

    pass


class DiscoveryBiomarkerViewSet(DiscoveryMixin, BaseBiomarkerViewSet):
    """
    Retrieves a number of discovery biomarkers.
    """

    pass


class DiscoveryComorbidityViewSet(DiscoveryMixin, BaseComorbidityViewSet):
    """
    Retrieves a number of discovery comorbidities.
    """

    pass


class DiscoveryExposureViewSet(DiscoveryMixin, BaseExposureViewSet):
    """
    Retrieves a number of discovery exposures.
    """

    pass


###############################################
#                                             #
#        CUSTOM OVERVIEW API ENDPOINTS        #
#                                             #
###############################################


class SidebarListViewSet(viewsets.ViewSet):
    """
    A viewset that provides a list of queryable names for various treatments and drugs.
    """

    @extend_schema(
        responses={201: OpenApiTypes.STR},
    )
    def list(self, request):
        """
        Retrieve the list of available values for all fields (including for
        datasets that the user is not authorized to view)
        """
        # Drugs queryable for chemotherapy
        chemotherapy_drug_names = (
            Chemotherapy.objects.exclude(drug_name__isnull=True)
            .values_list("drug_name", flat=True)
            .order_by("drug_name")
            .distinct()
        )
        # Drugs queryable for immunotherapy
        immunotherapy_drug_names = (
            Immunotherapy.objects.exclude(drug_name__isnull=True)
            .values_list("drug_name", flat=True)
            .order_by("drug_name")
            .distinct()
        )

        # Drugs queryable for hormone therapy
        hormone_therapy_drug_names = (
            HormoneTherapy.objects.exclude(drug_name__isnull=True)
            .values_list("drug_name", flat=True)
            .order_by("drug_name")
            .distinct()
        )

        # Create a dictionary of results
        results = {
            "treatment_types": TREATMENT_TYPE,
            "tumour_primary_sites": PRIMARY_SITE,
            "chemotherapy_drug_names": chemotherapy_drug_names,
            "immunotherapy_drug_names": immunotherapy_drug_names,
            "hormone_therapy_drug_names": hormone_therapy_drug_names,
        }

        # Return the results as a JSON response
        return Response(results)


@extend_schema(
    description="MoH cohorts count",
    responses={
        200: inline_serializer(
            name="moh_overview_cohort_count_response",
            fields={
                "cohort_count": serializers.IntegerField(),
            },
        )
    },
)
@api_view(["GET"])
@throttle_classes([MoHRateThrottle])
def cohort_count(_request):
    """
    Return the number of cohorts in the database.
    """
    return Response({"cohort_count": Program.objects.count()})


@extend_schema(
    description="MoH patients per cohort count",
    responses={
        200: inline_serializer(
            name="moh_overview_patient_per_cohort_response",
            fields={
                "patients_per_cohort_count": serializers.IntegerField(),
            },
        )
    },
)
@api_view(["GET"])
@throttle_classes([MoHRateThrottle])
def patient_per_cohort_count(_request):
    """
    Return the number of patients per cohort in the database.
    """
    cohorts = Donor.objects.values_list("program_id", flat=True)
    return Response(count_terms(cohorts))


@extend_schema(
    description="MoH individuals count",
    responses={
        200: inline_serializer(
            name="moh_overview_individual_count_response",
            fields={
                "individual_count": serializers.IntegerField(),
            },
        )
    },
)
@api_view(["GET"])
@throttle_classes([MoHRateThrottle])
def individual_count(_request):
    """
    Return the number of individuals in the database.
    """
    return Response({"individual_count": Donor.objects.count()})


@extend_schema(
    description="MoH gender count",
    responses={
        200: inline_serializer(
            name="moh_overview_gender_count_response",
            fields={
                "gender_count": serializers.IntegerField(),
            },
        )
    },
)
@api_view(["GET"])
@throttle_classes([MoHRateThrottle])
def gender_count(_request):
    """
    Return the count for every gender in the database.
    """
    genders = Donor.objects.values_list("gender", flat=True)
    return Response(count_terms(genders))


@extend_schema(
    description="MoH cancer types count",
    responses={
        200: inline_serializer(
            name="moh_overview_cancer_type_count_response",
            fields={
                "cancer_type_count": serializers.IntegerField(),
            },
        )
    },
)
@api_view(["GET"])
@throttle_classes([MoHRateThrottle])
def cancer_type_count(_request):
    """
    Return the count for every cancer type in the database.
    """
    cancer_types = list(Donor.objects.values_list("primary_site", flat=True))

    # Handle missing values as empty arrays
    for i in range(len(cancer_types)):
        if cancer_types[i] is None:
            cancer_types[i] = [None]

    return Response(count_terms(cancer_types))


@extend_schema(
    description="MoH Treatments type count",
    responses={
        200: inline_serializer(
            name="moh_overview_treatment_type_count_response",
            fields={
                "treatment_type_count": serializers.IntegerField(),
            },
        )
    },
)
@api_view(["GET"])
@throttle_classes([MoHRateThrottle])
def treatment_type_count(_request):
    """
    Return the count for every treatment type in the database.
    """
    treatment_types = list(Treatment.objects.values_list("treatment_type", flat=True))

    # Handle missing values as empty arrays
    for i in range(len(treatment_types)):
        if treatment_types[i] is None:
            treatment_types[i] = [None]

    return Response(count_terms(treatment_types))


@extend_schema(
    description="MoH Diagnosis age count",
    responses={
        200: inline_serializer(
            name="moh_overview_diagnosis_age_count_response",
            fields={
                "age_range_count": serializers.IntegerField(),
            },
        )
    },
)
@api_view(["GET"])
@throttle_classes([MoHRateThrottle])
def diagnosis_age_count(_request):
    """
    Return the count for age of diagnosis in the database.
    """
    # Find the earliest diagnosis date per donor
    diagnosis_dates = PrimaryDiagnosis.objects.values(
        "submitter_donor_id", "date_of_diagnosis"
    )
    min_dates = {}
    for d_date in diagnosis_dates:
        donor = d_date["submitter_donor_id"]
        cur_date = (
            datetime.strptime(d_date["date_of_diagnosis"], "%Y-%m").date()
            if d_date["date_of_diagnosis"] is not None
            else date.max
        )
        if donor not in min_dates.keys():
            min_dates[donor] = cur_date
        else:
            if cur_date < min_dates[donor]:
                min_dates[donor] = cur_date

    # Calculate donor's age of diagnosis
    birth_dates = Donor.objects.values("submitter_donor_id", "date_of_birth")
    birth_dates = {
        date["submitter_donor_id"]: date["date_of_birth"] for date in birth_dates
    }
    ages = {}
    for donor, diagnosis_date in min_dates.items():
        if birth_dates[donor] is not None and diagnosis_date is not date.max:
            birth_date = datetime.strptime(birth_dates[donor], "%Y-%m").date()
            ages[donor] = (diagnosis_date - birth_date).days // 365.25
        else:
            ages[donor] = None

    age_counts = defaultdict(int)
    for age in ages.values():
        if age is None:
            age_counts["null"] += 1
        elif age <= 19:
            age_counts["0-19"] += 1
        elif age <= 29:
            age_counts["20-29"] += 1
        elif age <= 39:
            age_counts["30-39"] += 1
        elif age <= 49:
            age_counts["40-49"] += 1
        elif age <= 59:
            age_counts["50-59"] += 1
        elif age <= 69:
            age_counts["60-69"] += 1
        elif age <= 79:
            age_counts["70-79"] += 1
        else:
            age_counts["80+"] += 1

    return Response(age_counts)


@extend_schema(
    responses={200: OpenApiTypes.STR},
)
@api_view(["GET"])
def service_info(_request):
    schema_url = get_schema_url()

    return JsonResponse(
        {
            "name": "katsu",
            "description": "A CanDIG clinical data service",
            "version": settings.KATSU_VERSION,
            "schema_url": schema_url,
        },
        status=status.HTTP_200_OK,
        safe=False,
        json_dumps_params={"indent": 2},
    )


# ===========================================================

discovery_router = Router()
overview_router = Router()
# api.add_router("/discovery/", discovery_router, tags=["discovery"])
discovery_router.add_router("/overview/", overview_router, tags=["overview"])


def count_donors(model: Type[Model], filters=None) -> Dict[str, int]:
    queryset = model.objects.all()
    if model == Donor:
        count_field = "uuid"
    else:
        count_field = "donor_uuid"

    if filters is not None:
        queryset = filters.filter(queryset)

    item_counts = (
        queryset.values("program_id")
        .annotate(donor_count=Count(count_field, distinct=True))
        .order_by("program_id")
    )

    return {f"{item['program_id']}": item["donor_count"] for item in item_counts}


@discovery_router.get("/programs/", response=List[ProgramDiscoverySchema])
def discover_programs(request):
    programs = Program.objects.all()
    return list(programs)


@discovery_router.get("/donors/", response=DiscoverySchema)
def discover_donors(request, filters: DonorFilterSchema = Query(...)):
    donors = count_donors(Donor, filters)
    return DiscoverySchema(discovery_donor=donors)


@discovery_router.get("/specimen/", response=DiscoverySchema)
def discover_specimens(request, filters: SpecimenFilterSchema = Query(...)):
    specimens = count_donors(Specimen, filters)
    return DiscoverySchema(discovery_donor=specimens)


@discovery_router.get("/sample_registrations/", response=DiscoverySchema)
def discover_sample_registrations(request):
    sample_registrations = count_donors(SampleRegistration)
    return DiscoverySchema(discovery_donor=sample_registrations)


@discovery_router.get("/primary_diagnoses/", response=DiscoverySchema)
def discover_primary_diagnoses(request):
    primary_diagnoses = count_donors(PrimaryDiagnosis)
    return DiscoverySchema(discovery_donor=primary_diagnoses)


@discovery_router.get("/treatments/", response=DiscoverySchema)
def discover_treatments(request):
    treatments = count_donors(Treatment)
    return DiscoverySchema(discovery_donor=treatments)


@discovery_router.get("/chemotherapies/", response=DiscoverySchema)
def discover_chemotherapies(request):
    chemotherapies = count_donors(Chemotherapy)
    return DiscoverySchema(discovery_donor=chemotherapies)


@discovery_router.get("/hormone_therapies/", response=DiscoverySchema)
def discover_hormone_therapies(request):
    hormone_therapies = count_donors(HormoneTherapy)
    return DiscoverySchema(discovery_donor=hormone_therapies)


@discovery_router.get("/radiations/", response=DiscoverySchema)
def discover_radiations(request):
    radiations = count_donors(Radiation)
    return DiscoverySchema(discovery_donor=radiations)


@discovery_router.get("/immunotherapies/", response=DiscoverySchema)
def discover_immunotherapies(request):
    immunotherapies = count_donors(Immunotherapy)
    return DiscoverySchema(discovery_donor=immunotherapies)


@discovery_router.get("/surgeries/", response=DiscoverySchema)
def discover_surgeries(request):
    surgeries = count_donors(Surgery)
    return DiscoverySchema(discovery_donor=surgeries)


@discovery_router.get("/follow_ups/", response=DiscoverySchema)
def discover_follow_ups(request):
    follow_ups = count_donors(FollowUp)
    return DiscoverySchema(discovery_donor=follow_ups)


@discovery_router.get("/biomarkers/", response=DiscoverySchema)
def discover_biomarkers(request):
    biomarkers = count_donors(Biomarker)
    return DiscoverySchema(discovery_donor=biomarkers)


@discovery_router.get("/comorbidities/", response=DiscoverySchema)
def discover_comorbidities(request):
    comorbidities = count_donors(Comorbidity)
    return DiscoverySchema(discovery_donor=comorbidities)


@discovery_router.get("/exposures/", response=DiscoverySchema)
def discover_exposures(request):
    exposures = count_donors(Exposure)
    return DiscoverySchema(discovery_donor=exposures)


###############################################
#                                             #
#        CUSTOM OVERVIEW API ENDPOINTS        #
#                                             #
###############################################


@discovery_router.get("/sidebar_list/", response=Dict[str, Any])
def discover_sidebar_list(request):
    """
    Retrieve the list of available values for all fields (including for
    datasets that the user is not authorized to view)
    """
    # Drugs queryable for chemotherapy
    chemotherapy_drug_names = list(
        Chemotherapy.objects.exclude(drug_name__isnull=True)
        .values_list("drug_name", flat=True)
        .order_by("drug_name")
        .distinct()
    )
    # Drugs queryable for immunotherapy
    immunotherapy_drug_names = list(
        Immunotherapy.objects.exclude(drug_name__isnull=True)
        .values_list("drug_name", flat=True)
        .order_by("drug_name")
        .distinct()
    )

    # Drugs queryable for hormone therapy
    hormone_therapy_drug_names = list(
        HormoneTherapy.objects.exclude(drug_name__isnull=True)
        .values_list("drug_name", flat=True)
        .order_by("drug_name")
        .distinct()
    )

    # Create a dictionary of results
    results = {
        "treatment_types": TREATMENT_TYPE,
        "tumour_primary_sites": PRIMARY_SITE,
        "chemotherapy_drug_names": chemotherapy_drug_names,
        "immunotherapy_drug_names": immunotherapy_drug_names,
        "hormone_therapy_drug_names": hormone_therapy_drug_names,
    }

    return results


@overview_router.get("/cohort_count/", response=Dict[str, int])
def discover_cohort_count(request):
    """
    Return the number of cohorts in the database.
    """
    return {"cohort_count": Program.objects.count()}


@overview_router.get("/patients_per_cohort/", response=Dict[str, int])
def discover_patients_per_cohort(request):
    """
    Return the number of patients per cohort in the database.
    """
    cohorts = Donor.objects.values_list("program_id", flat=True)
    return count_terms(cohorts)


@overview_router.get("/individual_count/", response=Dict[str, int])
def discover_individual_count(request):
    """
    Return the number of individuals in the database.
    """

    return {"individual_count": Donor.objects.count()}


@overview_router.get("/gender_count/", response=Dict[str, int])
def discover_gender_count(request):
    """
    Return the count for every gender in the database.
    """
    genders = Donor.objects.values_list("gender", flat=True)
    return count_terms(genders)


@overview_router.get("/cancer_type_count/", response=Dict[str, int])
def discover_cancer_type_count(request):
    """
    Return the count for every cancer type in the database.
    """
    cancer_types = list(Donor.objects.values_list("primary_site", flat=True))

    # Handle missing values as empty arrays
    for i in range(len(cancer_types)):
        if cancer_types[i] is None:
            cancer_types[i] = [None]

    return count_terms(cancer_types)


@overview_router.get("/treatment_type_count/", response=Dict[str, int])
def discover_treatment_type_count(request):
    """
    Return the count for every treatment type in the database.
    """
    treatment_types = list(Treatment.objects.values_list("treatment_type", flat=True))

    # Handle missing values as empty arrays
    for i in range(len(treatment_types)):
        if treatment_types[i] is None:
            treatment_types[i] = [None]

    return count_terms(treatment_types)


@overview_router.get("/diagnosis_age_count/", response=Dict[str, int])
def discover_diagnosis_age_count(request):
    """
    Return the count for age of diagnosis in the database.
    If there are multiple date_of_diagnosis, get the earliest
    """
    age_count = {
        "null": 0,
        "0-19": 0,
        "20-29": 0,
        "30-39": 0,
        "40-49": 0,
        "50-59": 0,
        "60-69": 0,
        "70-79": 0,
        "80+": 0,
    }

    # For each donor, get diagnosis with earliest date
    earliest_diagnoses = (
        PrimaryDiagnosis.objects.values("donor_uuid")
        .annotate(earliest_date=Min("date_of_diagnosis"))
        .filter(earliest_date__isnull=False)
    )
    earliest_diagnoses_dict = {
        item["donor_uuid"]: item["earliest_date"] for item in earliest_diagnoses
    }

    # Create a dictionary to store donor UUIDs and their corresponding date_of_birth
    donor_dob_dict = {donor.uuid: donor.date_of_birth for donor in Donor.objects.all()}

    # count donor in each age bucket
    for donor_uuid, dob in donor_dob_dict.items():
        diagnosis_date = earliest_diagnoses_dict.get(donor_uuid)
        if diagnosis_date is not None:
            dob_date = datetime.strptime(dob, "%Y-%m")
            diagnosis_date = datetime.strptime(
                earliest_diagnoses_dict[donor_uuid], "%Y-%m"
            )
            # Calculate age at time diagnosis
            age = diagnosis_date.year - dob_date.year

            if age < 20:
                age_count["0-19"] += 1
            elif age < 30:
                age_count["20-29"] += 1
            elif age < 40:
                age_count["30-39"] += 1
            elif age < 50:
                age_count["40-49"] += 1
            elif age < 60:
                age_count["50-59"] += 1
            elif age < 70:
                age_count["60-69"] += 1
            elif age < 80:
                age_count["70-79"] += 1
            else:
                age_count["80+"] += 1
        else:
            age_count["null"] += 1

    return age_count
