from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import mixins, serializers, viewsets
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
    BaseProgramViewSet,
    BaseRadiationViewSet,
    BaseSampleRegistrationViewSet,
    BaseSpecimenViewSet,
    BaseSurgeryViewSet,
    BaseTreatmentViewSet,
)
from chord_metadata_service.mohpackets.models import Biomarker, Donor, Program
from chord_metadata_service.mohpackets.serializers_nested import (
    DonorWithClinicalDataSerializer,
)
from chord_metadata_service.mohpackets.throttling import MoHRateThrottle
from chord_metadata_service.mohpackets.utils import get_authorized_datasets

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
    This mixin should be used for viewsets that need to restrict
    access to certain objects based on the user's permissions.

    Methods
    -------
    get_queryset()
        Returns a queryset that includes only the objects that the user is
        authorized to see.
    """

    def get_queryset(self):
        authorized_datasets = get_authorized_datasets(self.request)
        filtered_queryset = (
            super().get_queryset().filter(program_id__name__in=authorized_datasets)
        )
        return filtered_queryset


##############################################
#                                            #
#           AUTHORIZED API VIEWS             #
#                                            #
##############################################


class AuthorizedProgramViewSet(BaseProgramViewSet):
    def get_queryset(self):
        """
        Filter by the datasets that the user is authorized to see.
        """
        authorized_datasets = get_authorized_datasets(self.request)
        queryset = Program.objects.filter(name__in=authorized_datasets)
        return queryset


class AuthorizedDonorViewSet(AuthorizedMixin, BaseDonorViewSet):
    pass


class AuthorizedSpecimenViewSet(AuthorizedMixin, BaseSpecimenViewSet):
    pass


class AuthorizedSampleRegistrationViewSet(
    AuthorizedMixin, BaseSampleRegistrationViewSet
):
    pass


class AuthorizedPrimaryDiagnosisViewSet(AuthorizedMixin, BasePrimaryDiagnosisViewSet):
    pass


class AuthorizedTreatmentViewSet(AuthorizedMixin, BaseTreatmentViewSet):
    pass


class AuthorizedChemotherapyViewSet(AuthorizedMixin, BaseChemotherapyViewSet):
    pass


class AuthorizedHormoneTherapyViewSet(AuthorizedMixin, BaseHormoneTherapyViewSet):
    pass


class AuthorizedRadiationViewSet(AuthorizedMixin, BaseRadiationViewSet):
    pass


class AuthorizedImmunotherapyViewSet(AuthorizedMixin, BaseImmunotherapyViewSet):
    pass


class AuthorizedSurgeryViewSet(AuthorizedMixin, BaseSurgeryViewSet):
    pass


class AuthorizedFollowUpViewSet(AuthorizedMixin, BaseFollowUpViewSet):
    pass


class AuthorizedBiomarkerViewSet(AuthorizedMixin, BaseBiomarkerViewSet):
    pass


class AuthorizedComorbidityViewSet(AuthorizedMixin, BaseComorbidityViewSet):
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


class AuthorizedDonorWithClinicalDataViewSet(
    mixins.ListModelMixin, viewsets.GenericViewSet
):
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

    queryset = Donor.objects.prefetch_related(
        donor_biomarkers_prefetch,
        primary_diagnosis_biomarkers_prefetch,
        specimen_biomarkers_prefetch,
        treatment_biomarkers_prefetch,
        followup_biomarkers_prefetch,
        "comorbidity_set",
        "primarydiagnosis_set__treatment_set__chemotherapy_set",
        "primarydiagnosis_set__treatment_set__hormonetherapy_set",
        "primarydiagnosis_set__treatment_set__immunotherapy_set",
        "primarydiagnosis_set__treatment_set__radiation",
        "primarydiagnosis_set__treatment_set__surgery",
        "primarydiagnosis_set__treatment_set__followup_set",
        "primarydiagnosis_set__specimen_set__sampleregistration_set",
    ).all()