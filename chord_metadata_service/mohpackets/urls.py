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
ingest_router = routers.SimpleRouter()
ingest_router.register(r"programs", ingest_programs)
ingest_router.register(r"donors", ingest_donors)
ingest_router.register(r"specimens", ingest_specimens)
ingest_router.register(r"sample_registrations", ingest_sample_registrations)
ingest_router.register(r"primary_diagnoses", ingest_primary_diagnosises)
ingest_router.register(r"treatments", ingest_treatments)
ingest_router.register(r"chemotherapies", ingest_chemotherapies)
ingest_router.register(r"hormone_therapies", ingest_hormonetherapies)
ingest_router.register(r"radiations", ingest_radiations)
ingest_router.register(r"immunotherapies", ingest_immunotherapies)
ingest_router.register(r"surgeries", ingest_surgeries)
ingest_router.register(r"follow_ups", ingest_followups)
ingest_router.register(r"biomarkers", ingest_biomarkers)
ingest_router.register(r"comorbidities", ingest_comorbidities)

urlpatterns = [
    path("moh/", include(router.urls)),
    path("discovery/", include(discovery_router.urls)),
    path("ingest/", include(ingest_router.urls)),
    path("discovery/overview", moh_overview),
]
