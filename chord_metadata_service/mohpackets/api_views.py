from django.db.models import Prefetch
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, serializers, viewsets
from rest_framework.decorators import action, api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from chord_metadata_service.mohpackets.filters import (
    BiomarkerFilter,
    ChemotherapyFilter,
    ComorbidityFilter,
    DonorFilter,
    FollowUpFilter,
    HormoneTherapyFilter,
    ImmunotherapyFilter,
    PrimaryDiagnosisFilter,
    ProgramFilter,
    RadiationFilter,
    SampleRegistrationFilter,
    SpecimenFilter,
    SurgeryFilter,
    TreatmentFilter,
)
from chord_metadata_service.mohpackets.models import (
    Biomarker,
    Chemotherapy,
    Comorbidity,
    Donor,
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
from chord_metadata_service.mohpackets.pagination import StandardResultsSetPagination
from chord_metadata_service.mohpackets.permissions import CanDIGAdminOrReadOnly
from chord_metadata_service.mohpackets.serializers import (
    BiomarkerSerializer,
    ChemotherapySerializer,
    ComorbiditySerializer,
    DonorRelatedClinicalDataSerializer,
    DonorSerializer,
    FollowUpSerializer,
    HormoneTherapySerializer,
    ImmunotherapySerializer,
    PrimaryDiagnosisSerializer,
    ProgramSerializer,
    RadiationSerializer,
    SampleRegistrationSerializer,
    SpecimenSerializer,
    SurgerySerializer,
    TreatmentSerializer,
)
from chord_metadata_service.mohpackets.throttling import MoHRateThrottle
from chord_metadata_service.mohpackets.utils import get_authorized_datasets

"""
    This Views module uses ModelViewSet from Django Rest Framework.

    The ModelViewSet class inherits from GenericAPIView and includes implementations
    for various actions, by mixing in the behavior of the various mixin classes.

    The actions provided by the ModelViewSet class are
    .list(), .retrieve(), .create(), .update(), .partial_update(), and .destroy().

    For more information, see https://www.django-rest-framework.org/api-guide/viewsets/#modelviewset
"""

#########################################
#                                       #
#           HELPER FUNCTIONS            #
#                                       #
#########################################


def filter_by_authorized_datasets(request, queryset):
    """
    Filters by the datasets that the user is authorized to see.
    For example, if the user is authorized to datasets 1, 2, and 3,
    then the queryset will only include the results from those datasets.
    """
    authorized_datasets = get_authorized_datasets(request)
    filtered_dataset = queryset.filter(program_id__name__in=authorized_datasets)
    return filtered_dataset


####################################
#                                  #
#            API VIEWS             #
#                                  #
####################################


class ProgramViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProgramSerializer
    filterset_class = ProgramFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = Program.objects.all()

    def get_queryset(self):
        """
        Filter by the datasets that the user is authorized to see.
        """
        authorized_datasets = get_authorized_datasets(self.request)
        filtered_dataset = self.queryset.filter(name__in=authorized_datasets)
        return filtered_dataset


class DonorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DonorSerializer
    filterset_class = DonorFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = Donor.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class SpecimenViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SpecimenSerializer
    filterset_class = SpecimenFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = Specimen.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class SampleRegistrationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SampleRegistrationSerializer
    filterset_class = SampleRegistrationFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = SampleRegistration.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class PrimaryDiagnosisViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PrimaryDiagnosisSerializer
    filterset_class = PrimaryDiagnosisFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = PrimaryDiagnosis.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class TreatmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TreatmentSerializer
    filterset_class = TreatmentFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = Treatment.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class ChemotherapyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChemotherapySerializer
    filterset_class = ChemotherapyFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = Chemotherapy.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class HormoneTherapyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HormoneTherapySerializer
    filterset_class = HormoneTherapyFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = HormoneTherapy.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class RadiationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RadiationSerializer
    filterset_class = RadiationFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = Radiation.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class ImmunotherapyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ImmunotherapySerializer
    filterset_class = ImmunotherapyFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = Immunotherapy.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class SurgeryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SurgerySerializer
    filterset_class = SurgeryFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = Surgery.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class FollowUpViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FollowUpSerializer
    filterset_class = FollowUpFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = FollowUp.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class BiomarkerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BiomarkerSerializer
    filterset_class = BiomarkerFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = Biomarker.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class ComorbidityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ComorbiditySerializer
    filterset_class = ComorbidityFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = Comorbidity.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


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


class DonorRelatedClinicalDataViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DonorRelatedClinicalDataSerializer
    # queryset = Donor.objects.all()
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
