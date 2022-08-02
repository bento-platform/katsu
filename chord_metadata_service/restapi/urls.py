from django.urls import path, include
from rest_framework import routers

from chord_metadata_service.chord import api_views as chord_views
from chord_metadata_service.experiments import api_views as experiment_views
from chord_metadata_service.mcode import api_views as mcode_views
from chord_metadata_service.patients import api_views as individual_views
from chord_metadata_service.phenopackets import api_views as phenopacket_views
from chord_metadata_service.phenopackets.autocomplete_views import (
    DiseaseTermAutocomplete,
    PhenotypicFeatureTypeAutocomplete,
    BiosampleSampledTissueAutocomplete
)
from chord_metadata_service.resources import api_views as resources_views
from .api_views import overview, mcode_overview, public_search_fields, public_overview

__all__ = ["router", "urlpatterns"]

router = routers.DefaultRouter(trailing_slash=False)

# CHORD app urls
router.register(r'projects', chord_views.ProjectViewSet)
router.register(r'datasets', chord_views.DatasetViewSet)
router.register(r'table_ownership', chord_views.TableOwnershipViewSet)
router.register(r'tables', chord_views.TableViewSet)

# Experiments app urls
router.register(r'experiments', experiment_views.ExperimentViewSet)
router.register(r'experimentresults', experiment_views.ExperimentResultViewSet)

# Patients app urls
router.register(r'individuals', individual_views.IndividualViewSet)
router.register(r'batch/individuals', individual_views.IndividualGetCSVViewSet, basename='batch_individuals_csv')

# Phenopackets app urls
router.register(r'phenotypicfeatures', phenopacket_views.PhenotypicFeatureViewSet)
router.register(r'procedures', phenopacket_views.ProcedureViewSet)
router.register(r'htsfiles', phenopacket_views.HtsFileViewSet)
router.register(r'genes', phenopacket_views.GeneViewSet)
router.register(r'variants', phenopacket_views.VariantViewSet)
router.register(r'diseases', phenopacket_views.DiseaseViewSet)
router.register(r'metadata', phenopacket_views.MetaDataViewSet)
router.register(r'biosamples', phenopacket_views.BiosampleViewSet)
router.register(r'phenopackets', phenopacket_views.PhenopacketViewSet)
router.register(r'genomicinterpretations', phenopacket_views.GenomicInterpretationViewSet)
router.register(r'diagnoses', phenopacket_views.DiagnosisViewSet)
router.register(r'interpretations', phenopacket_views.InterpretationViewSet)

# mCode app urls
router.register(r'geneticspecimens', mcode_views.GeneticSpecimenViewSet)
router.register(r'cancergeneticvariants', mcode_views.CancerGeneticVariantViewSet)
router.register(r'genomicregionsstudied', mcode_views.GenomicRegionStudiedViewSet)
router.register(r'genomicsreports', mcode_views.GenomicsReportViewSet)
router.register(r'labsvital', mcode_views.LabsVitalViewSet)
router.register(r'cancerconditions', mcode_views.CancerConditionViewSet)
router.register(r'tnmstaging', mcode_views.TNMStagingViewSet)
router.register(r'cancerrelatedprocedures', mcode_views.CancerRelatedProcedureViewSet)
router.register(r'medicationstatements', mcode_views.MedicationStatementViewSet)
router.register(r'mcodepackets', mcode_views.MCodePacketViewSet)

# Resources app urls
router.register(r'resources', resources_views.ResourceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # apps schemas
    path('chord_phenopacket_schema', phenopacket_views.get_chord_phenopacket_schema,
         name="chord-phenopacket-schema"),
    path('experiment_schema', experiment_views.get_experiment_schema,
         name="experiment-schema"),
    path('mcode_schema', mcode_views.get_mcode_schema,
         name="mcode-schema"),
    # overview
    path('overview', overview, name="overview"),
    # mcode overview
    path('mcode_overview', mcode_overview, name="mcode-overview"),
    # autocomplete URLs
    path('disease_term_autocomplete', DiseaseTermAutocomplete.as_view(), name='disease-term-autocomplete',),
    path('phenotypic_feature_type_autocomplete', PhenotypicFeatureTypeAutocomplete.as_view(),
         name='phenotypic-feature-type-autocomplete',),
    path('biosample_sampled_tissue_autocomplete', BiosampleSampledTissueAutocomplete.as_view(),
         name='biosample-sampled-tissue-autocomplete',),
    # public
    path('public', individual_views.PublicListIndividuals.as_view(),
         name='public',),
    # public search fields schema
    path('public_search_fields', public_search_fields, name='public-search-fields',),
    # public overview
    path('public_overview', public_overview, name='public-overview',),
]
