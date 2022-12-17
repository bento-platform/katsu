from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from authx.auth import get_opa_datasets, is_site_admin
from rest_framework import generics, mixins, views
import requests
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

###############################################
#                                             #
#           DISCOVERY API ENDPOINTS           #
#                                             #
###############################################

class DonorDiscoverViewSet(mixins.ListModelMixin, viewsets.GenericViewSet): 
    serializer_class = DonorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = DonorFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = Donor.objects.all()
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        count = queryset.values_list('submitter_donor_id').distinct().count()
        return Response({"number of patients":count})

class SpecimenDiscoveryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SpecimenSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SpecimenFilter
    permission_classes = [CanDIGAdminOrReadOnly]
    queryset = Specimen.objects.all()
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        count = queryset.values_list('submitter_donor_id').distinct().count()
        return Response({"number of patients":count})