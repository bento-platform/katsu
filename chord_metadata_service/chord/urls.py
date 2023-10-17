from django.urls import path

from . import views_data_types, views_search
from .export import views as views_export
from .ingest import views as views_ingest
from .workflows import views as views_workflow
from chord_metadata_service.chord.api_views import DatasetViewSet

urlpatterns = [
    path('workflows', views_workflow.workflow_list, name="workflows"),
    path('workflows/<slug:workflow_id>', views_workflow.workflow_item, name="workflow-detail"),
    path('workflows/<slug:workflow_id>.wdl', views_workflow.workflow_file, name="workflow-file"),

    path('private/export', views_export.export, name="export"),

    path('ingest/<str:dataset_id>/<str:workflow_id>', views_ingest.ingest_into_dataset, name="ingest-into-dataset"),

    path('data-types', views_data_types.data_type_list, name="data-type-list"),
    path('data-types/<str:data_type>', views_data_types.data_type_detail, name="data-type-detail"),
    path('data-types/<str:data_type>/schema', views_data_types.data_type_schema, name="data-type-schema"),
    # TODO: Consistent snake or kebab
    path('data-types/<str:data_type>/metadata_schema', views_data_types.data_type_metadata_schema,
         name="data-type-metadata-schema"),

    path('search', views_search.chord_search, name="search"),
    path('fhir-search', views_search.fhir_public_search, name="fhir-search"),
    path('private/fhir-search', views_search.fhir_private_search, name="fhir-private-search"),
    path('private/search', views_search.chord_private_search, name="private-search"),

    path('datasets', DatasetViewSet.as_view({'get': 'list'}), name="chord-dataset-list"),
    path('datasets/<str:dataset_id>', DatasetViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}),
         name="chord-dataset-detail"),
    path('datasets/<str:dataset_id>/summary', views_search.dataset_summary, name="chord-dataset-summary"),
    path('datasets/<str:dataset_id>/data-types/<str:data_type>', views_data_types.dataset_data_type,
         name="chord-dataset-data-type"),

    path('datasets/<str:dataset_id>/data-types', views_data_types.dataset_data_type_summary,
         name="chord-dataset-data-type-summary"),

    path('datasets/<str:dataset_id>/search', views_search.public_dataset_search, name="public-dataset-search"),
    path('private/datasets/<str:dataset_id>/search', views_search.private_dataset_search,
         name="private-dataset-search"),
]
