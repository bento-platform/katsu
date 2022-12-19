from rest_framework import viewsets
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from chord_metadata_service.mohpackets.permissions import CanDIGAdminOrReadOnly
from chord_metadata_service.mohpackets.utils import get_authorized_datasets

from chord_metadata_service.mohpackets.filters import (
    ProgramFilter,
    DonorFilter,
    SpecimenFilter,
    SampleRegistrationFilter,
    PrimaryDiagnosisFilter,
    TreatmentFilter,
    ChemotherapyFilter,
    HormoneTherapyFilter,
    RadiationFilter,
    ImmunotherapyFilter,
    SurgeryFilter,
    FollowUpFilter,
    BiomarkerFilter,
    ComorbidityFilter,
)
from chord_metadata_service.mohpackets.serializers import (
    ProgramSerializer,
    DonorSerializer,
    SpecimenSerializer,
    SampleRegistrationSerializer,
    PrimaryDiagnosisSerializer,
    TreatmentSerializer,
    ChemotherapySerializer,
    HormoneTherapySerializer,
    RadiationSerializer,
    ImmunotherapySerializer,
    SurgerySerializer,
    FollowUpSerializer,
    BiomarkerSerializer,
    ComorbiditySerializer,
)
from chord_metadata_service.mohpackets.models import (
    Program,
    Donor,
    Specimen,
    SampleRegistration,
    PrimaryDiagnosis,
    Treatment,
    Chemotherapy,
    HormoneTherapy,
    Radiation,
    Immunotherapy,
    Surgery,
    FollowUp,
    Biomarker,
    Comorbidity,
)


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
    filtered_dataset = queryset.filter(program_id__in=authorized_datasets)
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
    queryset = Program.objects.all()


class DonorViewSet(viewsets.ModelViewSet):
    serializer_class = DonorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = DonorFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = Donor.objects.all()

    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class SpecimenViewSet(viewsets.ModelViewSet):
    serializer_class = SpecimenSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SpecimenFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = Specimen.objects.all()
    
    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class SampleRegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = SampleRegistrationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SampleRegistrationFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = SampleRegistration.objects.all()
    
    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class PrimaryDiagnosisViewSet(viewsets.ModelViewSet):
    serializer_class = PrimaryDiagnosisSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PrimaryDiagnosisFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = PrimaryDiagnosis.objects.all()
    
    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class TreatmentViewSet(viewsets.ModelViewSet):
    serializer_class = TreatmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TreatmentFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = Treatment.objects.all()
    
    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class ChemotherapyViewSet(viewsets.ModelViewSet):
    serializer_class = ChemotherapySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ChemotherapyFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = Chemotherapy.objects.all()
    
    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class HormoneTherapyViewSet(viewsets.ModelViewSet):
    serializer_class = HormoneTherapySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = HormoneTherapyFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = HormoneTherapy.objects.all()
    
    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class RadiationViewSet(viewsets.ModelViewSet):
    serializer_class = RadiationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RadiationFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = Radiation.objects.all()
    
    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class ImmunotherapyViewSet(viewsets.ModelViewSet):
    serializer_class = ImmunotherapySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ImmunotherapyFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = Immunotherapy.objects.all()
    
    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class SurgeryViewSet(viewsets.ModelViewSet):
    serializer_class = SurgerySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SurgeryFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = Surgery.objects.all()
    
    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class FollowUpViewSet(viewsets.ModelViewSet):
    serializer_class = FollowUpSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = FollowUpFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = FollowUp.objects.all()
    
    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class BiomarkerViewSet(viewsets.ModelViewSet):
    serializer_class = BiomarkerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BiomarkerFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = Biomarker.objects.all()
    
    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


class ComorbidityViewSet(viewsets.ModelViewSet):
    serializer_class = ComorbiditySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ComorbidityFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = Comorbidity.objects.all()
    
    def get_queryset(self):
        return filter_by_authorized_datasets(self.request, self.queryset)


###############################################
#                                             #
#           CUSTOM API ENDPOINTS              #
#                                             #
###############################################

# TODO: redo this overview endpoint
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
