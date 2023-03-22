from django.urls import include, path
from rest_framework import routers

from chord_metadata_service.mohpackets.api_authorized import (
    AuthorizedBiomarkerViewSet,
    AuthorizedChemotherapyViewSet,
    AuthorizedComorbidityViewSet,
    AuthorizedDonorViewSet,
    AuthorizedDonorWithClinicalDataViewSet,
    AuthorizedFollowUpViewSet,
    AuthorizedHormoneTherapyViewSet,
    AuthorizedImmunotherapyViewSet,
    AuthorizedPrimaryDiagnosisViewSet,
    AuthorizedProgramViewSet,
    AuthorizedRadiationViewSet,
    AuthorizedSampleRegistrationViewSet,
    AuthorizedSpecimenViewSet,
    AuthorizedSurgeryViewSet,
    AuthorizedTreatmentViewSet,
    moh_overview,
)
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
from chord_metadata_service.mohpackets.api_ingest import (
    delete_all,
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
    version_check,
)

# ================== AUTHORIZED API ================== #
router = routers.SimpleRouter()
router.register(r"programs", AuthorizedProgramViewSet, basename="authorized_program")
router.register(r"donors", AuthorizedDonorViewSet)
router.register(r"specimens", AuthorizedSpecimenViewSet)
router.register(r"sample_registrations", AuthorizedSampleRegistrationViewSet)
router.register(r"primary_diagnoses", AuthorizedPrimaryDiagnosisViewSet)
router.register(r"treatments", AuthorizedTreatmentViewSet)
router.register(r"chemotherapies", AuthorizedChemotherapyViewSet)
router.register(r"hormone_therapies", AuthorizedHormoneTherapyViewSet)
router.register(r"radiations", AuthorizedRadiationViewSet)
router.register(r"immunotherapies", AuthorizedImmunotherapyViewSet)
router.register(r"surgeries", AuthorizedSurgeryViewSet)
router.register(r"follow_ups", AuthorizedFollowUpViewSet)
router.register(r"biomarkers", AuthorizedBiomarkerViewSet)
router.register(r"comorbidities", AuthorizedComorbidityViewSet)
router.register(r"donor_with_clinical_data", AuthorizedDonorWithClinicalDataViewSet)

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
    path("authorized/", include(router.urls)),
    path("discovery/", include(discovery_router.urls)),
    path("ingest/", include(ingest_patterns)),
    path("delete/all", delete_all),
    path("version_check", version_check),
    path("discovery/overview", moh_overview),
]