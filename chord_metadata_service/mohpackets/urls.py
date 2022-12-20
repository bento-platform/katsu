from rest_framework import routers
from django.urls import path, include
from chord_metadata_service.mohpackets.api_views import (
    ProgramViewSet,
    DonorViewSet,
    SpecimenViewSet,
    SampleRegistrationViewSet,
    PrimaryDiagnosisViewSet,
    TreatmentViewSet,
    ChemotherapyViewSet,
    HormoneTherapyViewSet,
    RadiationViewSet,
    ImmunotherapyViewSet,
    SurgeryViewSet,
    FollowUpViewSet,
    BiomarkerViewSet,
    ComorbidityViewSet,
)
from chord_metadata_service.mohpackets.api_discovery import (
    DiscoveryDonorViewSet,
    DiscoverySpecimenViewSet,
    DiscoverySampleRegistrationViewSet,
    DiscoveryPrimaryDiagnosisViewSet,
    DiscoveryTreatmentViewSet,
    DiscoveryChemotherapyViewSet,
    DiscoveryHormoneTherapyViewSet,
    DiscoveryRadiationViewSet,
    DiscoveryImmunotherapyViewSet,
    DiscoverySurgeryViewSet,
    DiscoveryFollowUpViewSet,
    DiscoveryBiomarkerViewSet,
    DiscoveryComorbidityViewSet,
)

# ================== MOH API ================== #
router = routers.SimpleRouter()
router.register(r"programs", ProgramViewSet)
router.register(r"donors", DonorViewSet)
router.register(r"specimens", SpecimenViewSet)
router.register(r"sample_registrations", SampleRegistrationViewSet)
router.register(r"primary_diagnoses", PrimaryDiagnosisViewSet)
router.register(r"treatments", TreatmentViewSet)
router.register(r"chemotherapies", ChemotherapyViewSet)
router.register(r"hormone_therapies", HormoneTherapyViewSet)
router.register(r"radiations", RadiationViewSet)
router.register(r"immunotherapies", ImmunotherapyViewSet)
router.register(r"surgeries", SurgeryViewSet)
router.register(r"follow_ups", FollowUpViewSet)
router.register(r"biomarkers", BiomarkerViewSet)
router.register(r"comorbidities", ComorbidityViewSet)
# urlpatterns = router.urls

# ================== DISCOVERY API ================== #
discovery_router = routers.SimpleRouter()
discovery_router.register(r"donors", DiscoveryDonorViewSet)
discovery_router.register(r"specimens", DiscoverySpecimenViewSet)
discovery_router.register(r"sample_registrations", DiscoverySampleRegistrationViewSet)
discovery_router.register(r"primary_diagnoses", DiscoveryPrimaryDiagnosisViewSet)
discovery_router.register(r"treatments", DiscoveryTreatmentViewSet)
discovery_router.register(r"chemotherapies", DiscoveryChemotherapyViewSet)
discovery_router.register(r"hormone_therapies", DiscoveryHormoneTherapyViewSet)
discovery_router.register(r"radiations", DiscoveryRadiationViewSet)
discovery_router.register(r"immunotherapies", DiscoveryImmunotherapyViewSet)
discovery_router.register(r"surgeries", DiscoverySurgeryViewSet)
discovery_router.register(r"follow_ups", DiscoveryFollowUpViewSet)
discovery_router.register(r"biomarkers", DiscoveryBiomarkerViewSet)
discovery_router.register(r"comorbidities", DiscoveryComorbidityViewSet)

urlpatterns = [
    path("moh/", include(router.urls)),
    path("discovery/", include(discovery_router.urls)),
]
