import itertools
import os

from django.apps import apps
from django.db.models import Prefetch
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import mixins, serializers, status, viewsets
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
    BaseProgramViewSet,
    BaseRadiationViewSet,
    BaseSampleRegistrationViewSet,
    BaseSpecimenViewSet,
    BaseSurgeryViewSet,
    BaseTreatmentViewSet,
)
from chord_metadata_service.mohpackets.authentication import (
    LocalAuthentication,
    TokenAuthentication,
)
from chord_metadata_service.mohpackets.models import (
    Biomarker,
    Chemotherapy,
    Donor,
    FollowUp,
    HormoneTherapy,
    Immunotherapy,
    Program,
    Treatment,
)
from chord_metadata_service.mohpackets.pagination import StandardResultsSetPagination
from chord_metadata_service.mohpackets.serializers_nested import (
    DonorWithClinicalDataSerializer,
)
from chord_metadata_service.mohpackets.throttling import MoHRateThrottle

"""
    This module inheriting from the base views and adding the authorized mixin,
    which returns the objects related to the datasets that the user is authorized to see.
"""


##########################################
#                                        #
#           HELPER FUNCTIONS             #
#                                        #
##########################################


class AuthorizedMixin:
    """
    This mixin should be used for viewsets that need to restrict access.

    The authentication classes are set based on the `DJANGO_SETTINGS_MODULE`.
    If the env is "dev" or "prod", the `TokenAuthentication` class is
    used. Otherwise, the `LocalAuthentication` class is used.

    Methods
    -------
    get_queryset()
        Returns a filtered queryset that includes only the objects that the user is
        authorized to see based on their permissions.
    """

    pagination_class = StandardResultsSetPagination
    settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
    auth_methods = []
    # Use jwt token auth in prod/dev environment
    if "dev" in settings_module or "prod" in settings_module:
        auth_methods.append(TokenAuthentication)
    else:
        auth_methods.append(LocalAuthentication)
    authentication_classes = auth_methods

    def get_queryset(self):
        authorized_datasets = self.request.authorized_datasets
        filtered_queryset = (
            super().get_queryset().filter(program_id__in=authorized_datasets)
        )
        return filtered_queryset


##############################################
#                                            #
#           AUTHORIZED API VIEWS             #
#                                            #
##############################################


class AuthorizedProgramViewSet(BaseProgramViewSet, mixins.DestroyModelMixin):
    # For Program, we want to be able to access all datasets but still need authorization
    pagination_class = StandardResultsSetPagination
    settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
    authentication_classes = [
        TokenAuthentication
        if "dev" in settings_module or "prod" in settings_module
        else LocalAuthentication
    ]


class AuthorizedDonorViewSet(AuthorizedMixin, BaseDonorViewSet):
    """
    Retrieves a list of authorized donors.
    """

    pass


class AuthorizedSpecimenViewSet(AuthorizedMixin, BaseSpecimenViewSet):
    """
    Retrieves a list of authorized specimens.
    """

    pass


class AuthorizedSampleRegistrationViewSet(
    AuthorizedMixin, BaseSampleRegistrationViewSet
):
    """
    Retrieves a list of authorized sample registrations.
    """

    pass


class AuthorizedPrimaryDiagnosisViewSet(AuthorizedMixin, BasePrimaryDiagnosisViewSet):
    """
    Retrieves a list of authorized primary diagnosises.
    """

    pass


class AuthorizedTreatmentViewSet(AuthorizedMixin, BaseTreatmentViewSet):
    """
    Retrieves a list of authorized treatments.
    """

    pass


class AuthorizedChemotherapyViewSet(AuthorizedMixin, BaseChemotherapyViewSet):
    """
    Retrieves a list of authorized chemotherapies.
    """

    pass


class AuthorizedHormoneTherapyViewSet(AuthorizedMixin, BaseHormoneTherapyViewSet):
    """
    Retrieves a list of authorized hormone therapies.
    """

    pass


class AuthorizedRadiationViewSet(AuthorizedMixin, BaseRadiationViewSet):
    """
    Retrieves a list of authorized radiations.
    """

    pass


class AuthorizedImmunotherapyViewSet(AuthorizedMixin, BaseImmunotherapyViewSet):
    """
    Retrieves a list of authorized immuno therapies.
    """

    pass


class AuthorizedSurgeryViewSet(AuthorizedMixin, BaseSurgeryViewSet):
    """
    Retrieves a list of authorized surgeries.
    """

    pass


class AuthorizedFollowUpViewSet(AuthorizedMixin, BaseFollowUpViewSet):
    """
    Retrieves a list of authorized follow ups.
    """

    pass


class AuthorizedBiomarkerViewSet(AuthorizedMixin, BaseBiomarkerViewSet):
    """
    Retrieves a list of authorized biomarkers.
    """

    pass


class AuthorizedComorbidityViewSet(AuthorizedMixin, BaseComorbidityViewSet):
    """
    Retrieves a list of authorized comorbidities.
    """

    pass


class AuthorizedExposureViewSet(AuthorizedMixin, BaseExposureViewSet):
    """
    Retrieves a list of authorized exposures.
    """

    pass


###############################################
#                                             #
#           CUSTOM API ENDPOINTS              #
#                                             #
###############################################


# TODO: redo this overview endpoint
@extend_schema(
    description="MoH Overview schema",
    responses={
        200: inline_serializer(
            name="moh_overview_schema_response",
            fields={
                "cohort_count": serializers.IntegerField(),
                "individual_count": serializers.IntegerField(),
            },
        )
    },
)
@api_view(["GET"])
@throttle_classes([MoHRateThrottle])
def moh_overview(_request):
    """
    Return a summary of the statistics for the database:
    - cohort_count: number of datasets
    - individual_count: number of individuals
    - ethnicity: the count of each ethenicity
    - gender: the count of each gender
    """
    return Response(
        {
            "cohort_count": Program.objects.count(),
            "individual_count": Donor.objects.count(),
            # where to get ethnicity and gender?
        }
    )


class CustomViewSet(viewsets.ViewSet):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="model",
                description="Model name",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="include_fields",
                description="Comma-separated list of included fields",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={201: OpenApiTypes.STR},
    )
    def list(self, request):
        model_name = request.query_params.get("model")
        include_fields = request.query_params.getlist("include_fields")

        try:
            model = apps.get_model("mohpackets", model_name)
        except LookupError:
            return Response(
                {"error": f"Model '{model_name}' not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = model.objects.values(*include_fields)

        return Response(queryset)


class QueryableNamesViewSet(viewsets.ViewSet):
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
        # Types of treatment queryable by name
        treatment_types_qs = (
            Treatment.objects.exclude(treatment_type__isnull=True)
            .values_list("treatment_type", flat=True)
            .order_by("treatment_type")
            .distinct()
        )

        # Flatten the list of treatment types
        treatment_types = set(itertools.chain.from_iterable(treatment_types_qs))

        # Tumour primary sites queryable by name
        tumour_primary_sites_qs = (
            Donor.objects.exclude(primary_site__isnull=True)
            .values_list("primary_site", flat=True)
            .order_by("primary_site")
            .distinct()
        )

        # Flatten the list of Tumour primary sites
        tumour_primary_sites = set(
            itertools.chain.from_iterable(tumour_primary_sites_qs)
        )

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
            "treatment_types": treatment_types,
            "tumour_primary_sites": tumour_primary_sites,
            "chemotherapy_drug_names": chemotherapy_drug_names,
            "immunotherapy_drug_names": immunotherapy_drug_names,
            "hormone_therapy_drug_names": hormone_therapy_drug_names,
        }

        # Return the results as a JSON response
        return Response(results)


@extend_schema_view(
    list=extend_schema(
        description="Retrieves a list of authorized Donor with clinical data."
    )
)
class AuthorizedDonorWithClinicalDataViewSet(AuthorizedMixin, BaseDonorViewSet):
    """
    This viewset provides access to Donor model and its related clinical data.
    It uses the DonorWithClinicalDataSerializer for serialization.

    The viewset pre-fetches related objects using the `prefetch_related` method
    to minimize database queries. This ensures that all the related objects are
    available in a single database query, improving the performance of the viewset.
    """

    serializer_class = DonorWithClinicalDataSerializer
    donor_biomarkers_prefetch = Prefetch(
        "biomarker_set",
        queryset=Biomarker.objects.filter(
            submitter_primary_diagnosis_id__isnull=True,
            submitter_specimen_id__isnull=True,
            submitter_treatment_id__isnull=True,
            submitter_follow_up_id__isnull=True,
        ),
    )
    primary_diagnosis_biomarkers_prefetch = Prefetch(
        "primarydiagnosis_set__biomarker_set",
        queryset=Biomarker.objects.filter(
            submitter_primary_diagnosis_id__isnull=False,
            submitter_specimen_id__isnull=True,
            submitter_treatment_id__isnull=True,
            submitter_follow_up_id__isnull=True,
        ),
    )
    specimen_biomarkers_prefetch = Prefetch(
        "primarydiagnosis_set__specimen_set__biomarker_set",
        queryset=Biomarker.objects.filter(
            submitter_specimen_id__isnull=False,
            submitter_follow_up_id__isnull=True,
        ),
    )
    treatment_biomarkers_prefetch = Prefetch(
        "primarydiagnosis_set__treatment_set__biomarker_set",
        queryset=Biomarker.objects.filter(
            submitter_treatment_id__isnull=False,
            submitter_follow_up_id__isnull=True,
        ),
    )
    followup_biomarkers_prefetch = Prefetch(
        "primarydiagnosis_set__treatment_set__followup_set__biomarker_set",
        queryset=Biomarker.objects.filter(
            submitter_follow_up_id__isnull=False,
        ),
    )

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
        donor_biomarkers_prefetch,
        primary_diagnosis_biomarkers_prefetch,
        specimen_biomarkers_prefetch,
        treatment_biomarkers_prefetch,
        followup_biomarkers_prefetch,
        donor_followups_prefetch,
        primary_diagnosis_followups_prefetch,
        "comorbidity_set",
        "primarydiagnosis_set__treatment_set__chemotherapy_set",
        "primarydiagnosis_set__treatment_set__hormonetherapy_set",
        "primarydiagnosis_set__treatment_set__immunotherapy_set",
        "primarydiagnosis_set__treatment_set__radiation",
        "primarydiagnosis_set__treatment_set__surgery",
        "primarydiagnosis_set__specimen_set__sampleregistration_set",
    ).all()
