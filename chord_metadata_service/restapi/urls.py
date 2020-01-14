from django.urls import path, include
from rest_framework import routers
from chord_metadata_service.chord import api_views as chord_views
from chord_metadata_service.patients import api_views as individual_views
from chord_metadata_service.phenopackets import api_views as phenopacket_views


# from .settings import DEBUG


router = routers.DefaultRouter(trailing_slash=False)

# Patients app urls
router.register(r'individuals', individual_views.IndividualViewSet)

# Phenopackets app urls
router.register(r'phenotypicfeatures', phenopacket_views.PhenotypicFeatureViewSet)
router.register(r'procedures', phenopacket_views.ProcedureViewSet)
router.register(r'htsfiles', phenopacket_views.HtsFileViewSet)
router.register(r'genes', phenopacket_views.GeneViewSet)
router.register(r'variants', phenopacket_views.VariantViewSet)
router.register(r'diseases', phenopacket_views.DiseaseViewSet)
router.register(r'resources', phenopacket_views.ResourceViewSet)
router.register(r'metadata', phenopacket_views.MetaDataViewSet)
router.register(r'biosamples', phenopacket_views.BiosampleViewSet)
router.register(r'phenopackets', phenopacket_views.PhenopacketViewSet)
router.register(r'genomicinterpretations', phenopacket_views.GenomicInterpretationViewSet)
router.register(r'diagnoses', phenopacket_views.DiagnosisViewSet)
router.register(r'interpretations', phenopacket_views.InterpretationViewSet)
router.register(r'projects', chord_views.ProjectViewSet)
router.register(r'datasets', chord_views.DatasetViewSet)
router.register(r'table_ownership', chord_views.TableOwnershipViewSet)

urlpatterns = [
	path('', include(router.urls)),
]
