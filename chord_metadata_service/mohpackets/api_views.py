from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, viewsets
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response

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


class ProgramViewSet(viewsets.ModelViewSet):
    serializer_class = ProgramSerializer
    filter_backends = [DjangoFilterBackend]
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


class DonorViewSet(viewsets.ModelViewSet):
    serializer_class = DonorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = DonorFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = Donor.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class SpecimenViewSet(viewsets.ModelViewSet):
    serializer_class = SpecimenSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SpecimenFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = Specimen.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class SampleRegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = SampleRegistrationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SampleRegistrationFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = SampleRegistration.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class PrimaryDiagnosisViewSet(viewsets.ModelViewSet):
    serializer_class = PrimaryDiagnosisSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PrimaryDiagnosisFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = PrimaryDiagnosis.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class TreatmentViewSet(viewsets.ModelViewSet):
    serializer_class = TreatmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TreatmentFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = Treatment.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class ChemotherapyViewSet(viewsets.ModelViewSet):
    serializer_class = ChemotherapySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ChemotherapyFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = Chemotherapy.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class HormoneTherapyViewSet(viewsets.ModelViewSet):
    serializer_class = HormoneTherapySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = HormoneTherapyFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = HormoneTherapy.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class RadiationViewSet(viewsets.ModelViewSet):
    serializer_class = RadiationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RadiationFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = Radiation.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class ImmunotherapyViewSet(viewsets.ModelViewSet):
    serializer_class = ImmunotherapySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ImmunotherapyFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = Immunotherapy.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class SurgeryViewSet(viewsets.ModelViewSet):
    serializer_class = SurgerySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SurgeryFilter
    # permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = Surgery.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class FollowUpViewSet(viewsets.ModelViewSet):
    serializer_class = FollowUpSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = FollowUpFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = FollowUp.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class BiomarkerViewSet(viewsets.ModelViewSet):
    serializer_class = BiomarkerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BiomarkerFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [MoHRateThrottle]
    queryset = Biomarker.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class ComorbidityViewSet(viewsets.ModelViewSet):
    serializer_class = ComorbiditySerializer
    filter_backends = [DjangoFilterBackend]
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
