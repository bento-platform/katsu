from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
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
from chord_metadata_service.mohpackets.permissions import CanDIGAdminOrReadOnly

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


class SpecimenViewSet(viewsets.ModelViewSet):
    serializer_class = SpecimenSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SpecimenFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = Specimen.objects.all()


class SampleRegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = SampleRegistrationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SampleRegistrationFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = SampleRegistration.objects.all()


class PrimaryDiagnosisViewSet(viewsets.ModelViewSet):
    serializer_class = PrimaryDiagnosisSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PrimaryDiagnosisFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = PrimaryDiagnosis.objects.all()


class TreatmentViewSet(viewsets.ModelViewSet):
    serializer_class = TreatmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TreatmentFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = Treatment.objects.all()


class ChemotherapyViewSet(viewsets.ModelViewSet):
    serializer_class = ChemotherapySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ChemotherapyFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = Chemotherapy.objects.all()


class HormoneTherapyViewSet(viewsets.ModelViewSet):
    serializer_class = HormoneTherapySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = HormoneTherapyFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = HormoneTherapy.objects.all()


class RadiationViewSet(viewsets.ModelViewSet):
    serializer_class = RadiationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RadiationFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = Radiation.objects.all()


class ImmunotherapyViewSet(viewsets.ModelViewSet):
    serializer_class = ImmunotherapySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ImmunotherapyFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = Immunotherapy.objects.all()


class SurgeryViewSet(viewsets.ModelViewSet):
    serializer_class = SurgerySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SurgeryFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = Surgery.objects.all()


class FollowUpViewSet(viewsets.ModelViewSet):
    serializer_class = FollowUpSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = FollowUpFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = FollowUp.objects.all()


class BiomarkerViewSet(viewsets.ModelViewSet):
    serializer_class = BiomarkerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BiomarkerFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = Biomarker.objects.all()


class ComorbidityViewSet(viewsets.ModelViewSet):
    serializer_class = ComorbiditySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ComorbidityFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = Comorbidity.objects.all()
