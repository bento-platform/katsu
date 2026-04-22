from django.urls import path, include
from rest_framework import routers

from chord_metadata_service.chord import api_views as chord_views
from chord_metadata_service.chord import views_data_types as chord_dt_views
from chord_metadata_service.chord import views_search as chord_search_views
from chord_metadata_service.discovery.api_views import (
    discovery_endpoint,
    discovery_matches,
    discovery_rules,
    discovery_search_fields,
    discovery_schema,
    discovery_ui_hints,
)
from chord_metadata_service.experiments import api_views as experiment_views
from chord_metadata_service.patients import api_views as individual_views
from chord_metadata_service.phenopackets import api_views as phenopacket_views
from chord_metadata_service.resources import api_views as resources_views
from chord_metadata_service.restapi.api_views import search_overview, extra_properties_schema_types
from chord_metadata_service.restapi.routers import BatchListRouter

__all__ = ["router", "batch_router", "urlpatterns"]

router = routers.DefaultRouter(trailing_slash=False)
batch_router = BatchListRouter()

# CHORD app urls
router.register(r'projects', chord_views.ProjectViewSet)
router.register(r'datasets', chord_views.DatasetViewSet, basename="dataset")
router.register(r'datasets_v2', chord_views.DatasetV2ViewSet, basename="dataset_v2")
router.register(r'project_json_schemas', chord_views.ProjectJsonSchemaViewSet)

# Experiments app urls
router.register(r"experiments", experiment_views.ExperimentViewSet, basename="experiments")
router.register(r"experimentresults", experiment_views.ExperimentResultViewSet, basename="experimentresults")
router.register(r"batch/experiments", experiment_views.ExperimentBatchViewSet, basename="batch/experiments")

# Patients app urls
router.register(r"individuals", individual_views.IndividualViewSet, basename="individuals")
batch_router.register(r"batch/individuals", individual_views.IndividualBatchViewSet, basename="batch/individuals")

# Biosamples app urls
router.register(r"batch/biosamples", phenopacket_views.BiosampleBatchViewSet, basename="batch/biosamples")

# Phenopackets app urls
router.register(r"biosamples", phenopacket_views.BiosampleViewSet, basename="biosamples")
router.register(r"phenopackets", phenopacket_views.PhenopacketViewSet, basename="phenopackets")

# Resources app urls
router.register(r"resources", resources_views.ResourceViewSet, basename="resource")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(batch_router.urls)),
    # datasets_v2 sub-routes (nested under api/)
    path("datasets_v2/<str:identifier>/summary", chord_search_views.dataset_v2_summary,
         name="dataset-v2-summary"),
    path("datasets_v2/<str:identifier>/data-types", chord_dt_views.dataset_v2_data_type_summary,
         name="dataset-v2-data-type-summary"),
    path("datasets_v2/<str:identifier>/data-types/<str:data_type>", chord_dt_views.dataset_v2_data_type,
         name="dataset-v2-data-type"),
    path("datasets_v2/<str:identifier>/translations",
         chord_views.DatasetV2TranslationViewSet.as_view({'get': 'list', 'post': 'create'}),
         name="dataset-v2-translation-list"),
    path("datasets_v2/<str:identifier>/translations/<str:language>",
         chord_views.DatasetV2TranslationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name="dataset-v2-translation-detail"),
    # apps schemas
    path("schemas/phenopacket", phenopacket_views.get_chord_phenopacket_schema, name="chord-phenopacket-schema"),
    path(
        "schemas/phenopacket/<path:subschema>",
        phenopacket_views.get_chord_phenopacket_subschema,
        name="chord-phenopacket-subschema",
    ),
    path("schemas/experiment", experiment_views.get_experiment_schema, name="experiment-schema"),
    path("schemas/experiment/<path:subschema>", experiment_views.get_experiment_subschema, name="experiment-subschema"),
    path("schemas/discovery", discovery_schema, name="discovery-schema"),
    # extra properties schema types
    path("extra_properties_schema_types", extra_properties_schema_types, name="extra-properties-schema-types"),
    # overviews (statistics)
    path("search_overview", search_overview, name="search-overview"),
    # discovery endpoints
    path("discovery", discovery_endpoint, name="discovery"),
    path("discovery_matches", discovery_matches, name="discovery-matches"),
    path("discovery_search_fields", discovery_search_fields, name="discovery-search-fields"),
    path("discovery_ui_hints", discovery_ui_hints, name="discovery-ui-hints"),
    path("public", individual_views.PublicListIndividuals.as_view(), name="public"),
    path("discovery_rules", discovery_rules, name="discovery-rules"),
]
