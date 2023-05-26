from rest_framework import mixins, viewsets

from chord_metadata_service.mohpackets.filters import (
    BiomarkerFilter,
    ChemotherapyFilter,
    ComorbidityFilter,
    DonorFilter,
    ExposureFilter,
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
from chord_metadata_service.mohpackets.permissions import CanDIGAdminOrReadOnly
from chord_metadata_service.mohpackets.serializers import (
    BiomarkerSerializer,
    ChemotherapySerializer,
    ComorbiditySerializer,
    DonorSerializer,
    ExposureSerializer,
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

"""
    This module contains the base view class for discovery and authorized views.

    The queryset filter is not implemented in this base class to force its implementation
    in the discovery and authorized views. Implementing the queryset filter in
    each view provides more control over the data that is returned and helps to
    prevent unintentional exposure of unauthorized data.
"""

########################################
#                                      #
#           BASE API VIEWS             #
#                                      #
########################################


class BaseProgramViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProgramSerializer
    filterset_class = ProgramFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    throttle_classes = [MoHRateThrottle]
    queryset = Program.objects.all()


class BaseDonorViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = DonorSerializer
    filterset_class = DonorFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    throttle_classes = [MoHRateThrottle]
    queryset = Donor.objects.all()


class BaseSpecimenViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SpecimenSerializer
    filterset_class = SpecimenFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    throttle_classes = [MoHRateThrottle]
    queryset = Specimen.objects.all()


class BaseSampleRegistrationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SampleRegistrationSerializer
    filterset_class = SampleRegistrationFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    throttle_classes = [MoHRateThrottle]
    queryset = SampleRegistration.objects.all()


class BasePrimaryDiagnosisViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PrimaryDiagnosisSerializer
    filterset_class = PrimaryDiagnosisFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    throttle_classes = [MoHRateThrottle]
    queryset = PrimaryDiagnosis.objects.all()


class BaseTreatmentViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = TreatmentSerializer
    filterset_class = TreatmentFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    throttle_classes = [MoHRateThrottle]
    queryset = Treatment.objects.all()


class BaseChemotherapyViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ChemotherapySerializer
    filterset_class = ChemotherapyFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    throttle_classes = [MoHRateThrottle]
    queryset = Chemotherapy.objects.all()


class BaseHormoneTherapyViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = HormoneTherapySerializer
    filterset_class = HormoneTherapyFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    throttle_classes = [MoHRateThrottle]
    queryset = HormoneTherapy.objects.all()


class BaseRadiationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = RadiationSerializer
    filterset_class = RadiationFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    throttle_classes = [MoHRateThrottle]
    queryset = Radiation.objects.all()


class BaseImmunotherapyViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ImmunotherapySerializer
    filterset_class = ImmunotherapyFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    throttle_classes = [MoHRateThrottle]
    queryset = Immunotherapy.objects.all()


class BaseSurgeryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SurgerySerializer
    filterset_class = SurgeryFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    throttle_classes = [MoHRateThrottle]
    queryset = Surgery.objects.all()


class BaseFollowUpViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = FollowUpSerializer
    filterset_class = FollowUpFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    throttle_classes = [MoHRateThrottle]
    queryset = FollowUp.objects.all()


class BaseBiomarkerViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = BiomarkerSerializer
    filterset_class = BiomarkerFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    throttle_classes = [MoHRateThrottle]
    queryset = Biomarker.objects.all()


class BaseComorbidityViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ComorbiditySerializer
    filterset_class = ComorbidityFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    throttle_classes = [MoHRateThrottle]
    queryset = Comorbidity.objects.all()


class BaseExposureViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ExposureSerializer
    filterset_class = ExposureFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    throttle_classes = [MoHRateThrottle]
    queryset = Exposure.objects.all()
