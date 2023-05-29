from django.urls import include, path
from rest_framework import routers

from chord_metadata_service.mohpackets.api_authorized import (
    AuthorizedBiomarkerViewSet,
    AuthorizedChemotherapyViewSet,
    AuthorizedComorbidityViewSet,
    AuthorizedDonorViewSet,
    AuthorizedDonorWithClinicalDataViewSet,
    AuthorizedExposureViewSet,
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
)
from chord_metadata_service.mohpackets.api_discovery import (
    DiscoveryBiomarkerViewSet,
    DiscoveryChemotherapyViewSet,
    DiscoveryComorbidityViewSet,
    DiscoveryDonorViewSet,
    DiscoveryExposureViewSet,
    DiscoveryFollowUpViewSet,
    DiscoveryHormoneTherapyViewSet,
    DiscoveryImmunotherapyViewSet,
    DiscoveryPrimaryDiagnosisViewSet,
    DiscoveryRadiationViewSet,
    DiscoverySampleRegistrationViewSet,
    DiscoverySpecimenViewSet,
    DiscoverySurgeryViewSet,
    DiscoveryTreatmentViewSet,
    cancer_type_count,
    cohort_count,
    diagnosis_age_count,
    gender_count,
    individual_count,
    patient_per_cohort_count,
    treatment_type_count,
)
from chord_metadata_service.mohpackets.api_ingest import (
    delete_all,
    IngestProgramViewSet,
    IngestDonorViewSet,
    IngestSpecimenViewSet,
    IngestSampleRegistrationViewSet,
    IngestPrimaryDiagnosisViewSet,
    IngestTreatmentViewSet,
    IngestChemotherapyViewSet,
    IngestHormoneTherapyViewSet,
    IngestRadiationViewSet,
    IngestImmunotherapyViewSet,
    IngestSurgeryViewSet,
    IngestFollowUpViewSet,
    IngestBiomarkerViewSet,
    IngestComorbidityViewSet,
    IngestExposureViewSet,
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
router.register(r"exposures", AuthorizedExposureViewSet)
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
discovery_router.register(r"exposures", DiscoveryExposureViewSet)


# ================== INGEST API ================== #
ingest_router = routers.SimpleRouter()
ingest_router.register(r"programs", IngestProgramViewSet, basename="ingest_programs")
ingest_router.register(r"donors", IngestDonorViewSet, basename="ingest_donors")
ingest_router.register(r"specimens", IngestSpecimenViewSet,  basename="ingest_specimens")
ingest_router.register(r"sample_registrations", IngestSampleRegistrationViewSet,  basename="ingest_registrations")
ingest_router.register(r"primary_diagnoses", IngestPrimaryDiagnosisViewSet,  basename="ingest_diagnoses")
ingest_router.register(r"treatments", IngestTreatmentViewSet, basename="ingest_treatments")
ingest_router.register(r"chemotherapies", IngestChemotherapyViewSet, basename="ingest_chemotherapies")
ingest_router.register(r"hormone_therapies", IngestHormoneTherapyViewSet, basename="ingest_hormone_therapies")
ingest_router.register(r"radiations", IngestRadiationViewSet, basename="ingest_radiations")
ingest_router.register(r"immunotherapies", IngestImmunotherapyViewSet, basename="ingest_immunotherapies")
ingest_router.register(r"surgeries", IngestSurgeryViewSet, basename="ingest_surgeries")
ingest_router.register(r"follow_ups", IngestFollowUpViewSet, basename="ingest_followups")
ingest_router.register(r"biomarkers", IngestBiomarkerViewSet, basename="ingest_biomarkers")
ingest_router.register(r"comorbidities", IngestComorbidityViewSet, basename="ingest_comorbidities")
ingest_router.register(r"exposures", IngestExposureViewSet, basename="ingest_exposures")

urlpatterns = [
    path("authorized/", include(router.urls)),
    path("discovery/", include(discovery_router.urls)),
    #path("ingest/", include(ingest_patterns)),
    path("ingest/", include(ingest_router.urls)),
    path("delete/all", delete_all),
    path("version_check", version_check),
    path(
        "discovery/overview/",
        include(
            [
                path("cohort_count", cohort_count),
                path("patients_per_cohort", patient_per_cohort_count),
                path("individual_count", individual_count),
                path("gender_count", gender_count),
                path("cancer_type_count", cancer_type_count),
                path("treatment_type_count", treatment_type_count),
                path("diagnosis_age_count", diagnosis_age_count),
            ]
        ),
    ),
]
# added to trigger test
