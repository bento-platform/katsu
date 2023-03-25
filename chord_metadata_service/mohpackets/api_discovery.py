from collections import Counter, defaultdict
from datetime import datetime as dt

from drf_spectacular.utils import extend_schema, extend_schema_serializer, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response

from chord_metadata_service.mohpackets.api_base import (
    BaseBiomarkerViewSet,
    BaseChemotherapyViewSet,
    BaseComorbidityViewSet,
    BaseDonorViewSet,
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
    Donor,
    PrimaryDiagnosis,
    Program,
    SampleRegistration,
    Treatment,
)
from chord_metadata_service.mohpackets.throttling import MoHRateThrottle

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
        count = queryset.values_list("submitter_donor_id").distinct().count()
        return Response({"discovery_donor": count})


def count_terms(terms):
    """
    Return a dictionary of counts for every term in a list, used in overview endpoints
    for fields with lists as entries.
    """
    if isinstance(terms[0], list):  # Unnest list if nested
        terms = sum(terms, [])
    return Counter(terms)


###############################################
#                                             #
#           DISCOVERY API VIEWS               #
#                                             #
###############################################


class DiscoveryDonorViewSet(DiscoveryMixin, BaseDonorViewSet):
    pass


class DiscoverySpecimenViewSet(DiscoveryMixin, BaseSpecimenViewSet):
    pass


class DiscoverySampleRegistrationViewSet(DiscoveryMixin, BaseSampleRegistrationViewSet):
    pass


class DiscoveryPrimaryDiagnosisViewSet(DiscoveryMixin, BasePrimaryDiagnosisViewSet):
    pass


class DiscoveryTreatmentViewSet(DiscoveryMixin, BaseTreatmentViewSet):
    pass


class DiscoveryChemotherapyViewSet(DiscoveryMixin, BaseChemotherapyViewSet):
    pass


class DiscoveryHormoneTherapyViewSet(DiscoveryMixin, BaseHormoneTherapyViewSet):
    pass


class DiscoveryRadiationViewSet(DiscoveryMixin, BaseRadiationViewSet):
    pass


class DiscoveryImmunotherapyViewSet(DiscoveryMixin, BaseImmunotherapyViewSet):
    pass


class DiscoverySurgeryViewSet(DiscoveryMixin, BaseSurgeryViewSet):
    pass


class DiscoveryFollowUpViewSet(DiscoveryMixin, BaseFollowUpViewSet):
    pass


class DiscoveryBiomarkerViewSet(DiscoveryMixin, BaseBiomarkerViewSet):
    pass


class DiscoveryComorbidityViewSet(DiscoveryMixin, BaseComorbidityViewSet):
    pass


###############################################
#                                             #
#        CUSTOM OVERVIEW API ENDPOINTS        #
#                                             #
###############################################


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
    genders = SampleRegistration.objects.values_list("gender", flat=True)
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
    cancer_types = Donor.objects.values_list("primary_site", flat=True)
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
    treatment_types = Treatment.objects.values_list("treatment_type", flat=True)
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
    diagnosis_dates = PrimaryDiagnosis.objects.values("submitter_donor_id", "date_of_diagnosis")
    min_dates = {}
    for date in diagnosis_dates:
        donor = date["submitter_donor_id"]
        cur_date = (dt.strptime(date["date_of_diagnosis"], "%Y-%m").date()
                    if date["date_of_diagnosis"] != ''
                    else '')
        if donor not in min_dates.keys():
            min_dates[donor] = cur_date
        else:
            if ((min_dates[donor] != '' and cur_date < min_dates[donor]) or
               (min_dates[donor] == '' and cur_date != '')):
                min_dates[donor] = cur_date

    # Calculate donor's age of diagnosis
    birth_dates = Donor.objects.values("submitter_donor_id", "date_of_birth")
    birth_dates = {date["submitter_donor_id"]: date["date_of_birth"] for date in birth_dates}
    ages = {}
    for donor, diagnosis_date in min_dates.items():
        if birth_dates[donor] != '' and diagnosis_date != '':
            birth_date = dt.strptime(birth_dates[donor], "%Y-%m").date()
            ages[donor] = (diagnosis_date - birth_date).days // 365.25
        else:
            ages[donor] = ''

    age_counts = defaultdict(int)
    for age in ages.values():
        if age == '':
            age_counts["NA"] += 1
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
