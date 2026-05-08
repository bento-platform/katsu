from django.urls import path

from . import views_data_types, views_search
from .export import views as views_export
from .ingest import views as views_ingest
from .workflows import views as views_workflow
from chord_metadata_service.chord.api_views import DatasetViewSet, DatasetV2ViewSet, DatasetV2TranslationViewSet

urlpatterns = [
    path('workflows', views_workflow.workflow_list, name="workflows"),
    path('workflows/<slug:workflow_id>', views_workflow.workflow_item, name="workflow-detail"),
    path('workflows/<slug:workflow_id>.wdl', views_workflow.workflow_file, name="workflow-file"),

    path('private/export', views_export.export, name="export"),

    path('ingest-derived-experiment-results/<str:dataset_id>', views_ingest.ingest_derived_experiment_results,
         name="ingest-derived-experiment-results"),
    path('ingest/<str:dataset_id>/<str:workflow_id>', views_ingest.ingest_into_dataset, name="ingest-into-dataset"),

    path('data-types', views_data_types.data_type_list, name="data-type-list"),
    path('data-types/<str:data_type>', views_data_types.data_type_detail, name="data-type-detail"),
    path('data-types/<str:data_type>/schema', views_data_types.data_type_schema, name="data-type-schema"),
    # TODO: Consistent snake or kebab
    path('data-types/<str:data_type>/metadata_schema', views_data_types.data_type_metadata_schema,
         name="data-type-metadata-schema"),

    path('private/search', views_search.chord_private_search, name="private-search"),

    path('datasets', DatasetViewSet.as_view({'get': 'list'}), name="chord-dataset-list"),
    path('datasets/<str:dataset_id>', DatasetViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}),
         name="chord-dataset-detail"),

    path('datasets_v2', DatasetV2ViewSet.as_view({'get': 'list', 'post': 'create'}),
         name="chord-dataset-v2-list"),
    path('datasets_v2/<str:identifier>',
         DatasetV2ViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name="chord-dataset-v2-detail"),
    path('datasets_v2/<str:identifier>/summary',
         DatasetV2ViewSet.as_view({'get': 'summary'}),
         name="chord-dataset-v2-summary"),
    path('datasets_v2/<str:identifier>/data-types', views_data_types.dataset_v2_data_type_summary,
         name="chord-dataset-v2-data-type-summary"),
    path('datasets_v2/<str:identifier>/data-types/<str:data_type>', views_data_types.dataset_v2_data_type,
         name="chord-dataset-v2-data-type"),
    path('datasets_v2/<str:identifier>/translations',
         DatasetV2TranslationViewSet.as_view({'get': 'list', 'post': 'create'}),
         name="chord-dataset-v2-translation-list"),
    path('datasets_v2/<str:identifier>/translations/<str:language>',
         DatasetV2TranslationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name="chord-dataset-v2-translation-detail"),

    path('datasets/<str:dataset_id>/summary', views_search.dataset_summary, name="chord-dataset-summary"),
    path('datasets/<str:dataset_id>/data-types/<str:data_type>', views_data_types.dataset_data_type,
         name="chord-dataset-data-type"),

    path('datasets/<str:dataset_id>/data-types', views_data_types.dataset_data_type_summary,
         name="chord-dataset-data-type-summary"),

    path('private/datasets/<str:dataset_id>/search', views_search.private_dataset_search,
         name="private-dataset-search"),
]
