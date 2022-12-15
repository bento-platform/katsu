from rest_framework import routers
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

router = routers.SimpleRouter()
router.register(r'programs', ProgramViewSet)
router.register(r'donors', DonorViewSet)
router.register(r'specimens', SpecimenViewSet)
router.register(r'sample_registrations', SampleRegistrationViewSet)
router.register(r'primary_diagnoses', PrimaryDiagnosisViewSet)
router.register(r'treatments', TreatmentViewSet)
router.register(r'chemotherapies', ChemotherapyViewSet)
router.register(r'hormone_therapies', HormoneTherapyViewSet)
router.register(r'radiations', RadiationViewSet)
router.register(r'immunotherapies', ImmunotherapyViewSet)
router.register(r'surgeries', SurgeryViewSet)
router.register(r'follow_ups', FollowUpViewSet)
router.register(r'biomarkers', BiomarkerViewSet)
router.register(r'comorbidities', ComorbidityViewSet)
urlpatterns = router.urls
