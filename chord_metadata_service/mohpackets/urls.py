from django.urls import include, path
from rest_framework import routers

from chord_metadata_service.mohpackets.api_discovery import (
    DiscoveryBiomarkerViewSet,
    DiscoveryChemotherapyViewSet,
    DiscoveryComorbidityViewSet,
    DiscoveryDonorViewSet,
    DiscoveryFollowUpViewSet,
    DiscoveryHormoneTherapyViewSet,
    DiscoveryImmunotherapyViewSet,
    DiscoveryPrimaryDiagnosisViewSet,
    DiscoveryRadiationViewSet,
    DiscoverySampleRegistrationViewSet,
    DiscoverySpecimenViewSet,
    DiscoverySurgeryViewSet,
    DiscoveryTreatmentViewSet,
)
from chord_metadata_service.mohpackets.api_views import (
    BiomarkerViewSet,
    ChemotherapyViewSet,
    ComorbidityViewSet,
    DonorViewSet,
    FollowUpViewSet,
    HormoneTherapyViewSet,
    ImmunotherapyViewSet,
    PrimaryDiagnosisViewSet,
    ProgramViewSet,
    RadiationViewSet,
    SampleRegistrationViewSet,
    SpecimenViewSet,
    SurgeryViewSet,
    TreatmentViewSet,
    moh_overview,
)
from chord_metadata_service.mohpackets.ingest import (
    ingest_biomarkers,
    ingest_chemotherapies,
    ingest_comorbidities,
    ingest_donors,
    ingest_followups,
    ingest_hormonetherapies,
    ingest_immunotherapies,
    ingest_primary_diagnosises,
    ingest_programs,
    ingest_radiations,
    ingest_sample_registrations,
    ingest_specimens,
    ingest_surgeries,
    ingest_treatments,
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

# ================== INGEST API ================== #
ingest_patterns = [
    path("programs", ingest_programs),
    path("donors", ingest_donors),
    path("specimens", ingest_specimens),
    path("sample_registrations", ingest_sample_registrations),
    path("primary_diagnoses", ingest_primary_diagnosises),
    path("treatments", ingest_treatments),
    path("chemotherapies", ingest_chemotherapies),
    path("hormone_therapies", ingest_hormonetherapies),
    path("radiations", ingest_radiations),
    path("immunotherapies", ingest_immunotherapies),
    path("surgeries", ingest_surgeries),
    path("follow_ups", ingest_followups),
    path("biomarkers", ingest_biomarkers),
    path("comorbidities", ingest_comorbidities),
]

urlpatterns = [
    path("moh/", include(router.urls)),
    path("discovery/", include(discovery_router.urls)),
    path("ingest/", include(ingest_patterns)),
    path("discovery/overview", moh_overview),
]
