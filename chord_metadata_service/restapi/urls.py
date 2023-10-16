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
from .api_views import (
     overview,
     mcode_overview,
     public_search_fields,
     public_overview,
     public_dataset,
     search_overview,
     extra_properties_schema_types,
)
from chord_metadata_service.restapi.routers import BatchListRouter

__all__ = ["router", "batch_router", "urlpatterns"]

router = routers.DefaultRouter(trailing_slash=False)
batch_router = BatchListRouter()

# CHORD app urls
router.register(r'projects', chord_views.ProjectViewSet)
router.register(r'datasets', chord_views.DatasetViewSet, basename="datasets")
router.register(r'project_json_schemas', chord_views.ProjectJsonSchemaViewSet)

# Experiments app urls
router.register(r'experiments', experiment_views.ExperimentViewSet)
router.register(r'experimentresults', experiment_views.ExperimentResultViewSet)
router.register(r'batch/experiments', experiment_views.ExperimentBatchViewSet, basename="batch/experiments")

# Patients app urls
router.register(r'individuals', individual_views.IndividualViewSet, basename="individuals")
batch_router.register(r'batch/individuals', individual_views.IndividualBatchViewSet, basename="batch/individuals")

# Biosamples app urls
router.register(r'batch/biosamples', phenopacket_views.BiosampleBatchViewSet, basename="batch/biosamples")

# Phenopackets app urls
router.register(r'phenotypicfeatures', phenopacket_views.PhenotypicFeatureViewSet, basename="phenotypicfeatures")
router.register(r'htsfiles', phenopacket_views.HtsFileViewSet, basename="htsfiles")
router.register(r'genes', phenopacket_views.GeneViewSet, basename="genes")
router.register(r'diseases', phenopacket_views.DiseaseViewSet, basename="diseases")
router.register(r'metadata', phenopacket_views.MetaDataViewSet, basename="metadata")
router.register(r'biosamples', phenopacket_views.BiosampleViewSet, basename="biosamples")
router.register(r'phenopackets', phenopacket_views.PhenopacketViewSet, basename="phenopackets")
router.register(r'genomicinterpretations', phenopacket_views.GenomicInterpretationViewSet,
                basename="genomicinterpretations")
router.register(r'diagnoses', phenopacket_views.DiagnosisViewSet, basename="diagnoses")
router.register(r'interpretations', phenopacket_views.InterpretationViewSet, basename="interpretations")

# mCode app urls
router.register(r'geneticspecimens', mcode_views.GeneticSpecimenViewSet, basename="geneticspecimens")
router.register(r'cancergeneticvariants', mcode_views.CancerGeneticVariantViewSet, basename="cancergeneticvariants")
router.register(r'genomicregionsstudied', mcode_views.GenomicRegionStudiedViewSet, basename="genomicregionsstudied")
router.register(r'genomicsreports', mcode_views.GenomicsReportViewSet, basename="genomicsreports")
router.register(r'labsvital', mcode_views.LabsVitalViewSet, basename="labsvital")
router.register(r'cancerconditions', mcode_views.CancerConditionViewSet, basename="cancerconditions")
router.register(r'tnmstaging', mcode_views.TNMStagingViewSet, basename="tnmstaging")
router.register(r'cancerrelatedprocedures', mcode_views.CancerRelatedProcedureViewSet,
                basename="cancerrelatedprocedures")
router.register(r'medicationstatements', mcode_views.MedicationStatementViewSet, basename="medicationstatements")
router.register(r'mcodepackets', mcode_views.MCodePacketViewSet, basename="mcodepackets")

# Resources app urls
router.register(r'resources', resources_views.ResourceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include(batch_router.urls)),

    # apps schemas
    path('chord_phenopacket_schema', phenopacket_views.get_chord_phenopacket_schema,
         name="chord-phenopacket-schema"),
    path('experiment_schema', experiment_views.get_experiment_schema,
         name="experiment-schema"),
    path('mcode_schema', mcode_views.get_mcode_schema,
         name="mcode-schema"),

    # extra properties schema types
    path('extra_properties_schema_types', extra_properties_schema_types, name="extra-properties-schema-types"),

    # overviews (statistics)
    path('overview', overview, name="overview"),
    path('mcode_overview', mcode_overview, name="mcode-overview"),
    path('search_overview', search_overview, name="search-overview"),

    # autocomplete URLs
    path('disease_term_autocomplete', DiseaseTermAutocomplete.as_view(), name='disease-term-autocomplete',),
    path('phenotypic_feature_type_autocomplete', PhenotypicFeatureTypeAutocomplete.as_view(),
         name='phenotypic-feature-type-autocomplete',),
    path('biosample_sampled_tissue_autocomplete', BiosampleSampledTissueAutocomplete.as_view(),
         name='biosample-sampled-tissue-autocomplete',),

    # public endpoints (no confidential information leak)
    path('public', individual_views.PublicListIndividuals.as_view(),
         name='public',),
    path('public_search_fields', public_search_fields, name='public-search-fields',),
    path('public_overview', public_overview, name='public-overview',),
    path('public_dataset', public_dataset, name='public-dataset'),

    # uncensored endpoint for beacon search using fields from config.json
    path('beacon_search', individual_views.BeaconListIndividuals.as_view(), name='beacon-search'),
]
