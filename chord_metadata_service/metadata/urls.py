"""metadata URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from chord_metadata_service.restapi import api_views, views_ingest_fhir, urls as restapi_urls
from chord_metadata_service.chord import views_ingest, views_search
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.views import get_swagger_view

# TODO: django.conf.settings breaks reverse(), how to import properly?
from .settings import DEBUG

swagger_schema_view = get_swagger_view(title="Metadata Service API")

urlpatterns = [
    path('api/schema', get_schema_view(
        title="Metadata Service API",
        description="Metadata Service provides a phenotypic description of an Individual "
        "in the context of biomedical research.",
        version="0.1"
        ),
        name='openapi-schema'),
    path('', swagger_schema_view),
    path('api/', include(restapi_urls)),
    path('service-info', api_views.service_info, name="service-info"),

    path('workflows', views_ingest.workflow_list, name="workflows"),
    path('workflows/<slug:workflow_id>', views_ingest.workflow_item, name="workflow-detail"),
    path('workflows/<slug:workflow_id>.wdl', views_ingest.workflow_file, name="workflow-file"),

    path('private/ingest', views_ingest.ingest, name="ingest"),

    path('data-types', views_search.data_type_list, name="data-type-list"),
    path('data-types/phenopacket', views_search.data_type_phenopacket, name="data-type-detail"),
    path('data-types/phenopacket/schema', views_search.data_type_phenopacket_schema, name="data-type-schema"),
    # TODO: Consistent snake or kebab
    path('data-types/phenopacket/metadata_schema', views_search.data_type_phenopacket_metadata_schema,
         name="data-type-metadata-schema"),
    path('tables', views_search.table_list, name="table-list"),
    path('tables/<str:table_id>', views_search.table_detail, name="table-detail"),
    path('tables/<str:table_id>/summary', views_search.chord_table_summary, name="table-summary"),
    path('tables/<str:table_id>/search', views_search.chord_public_table_search, name="public-table-search"),
    path('search', views_search.chord_search, name="search"),
    path('fhir-search', views_search.fhir_public_search, name="fhir-search"),
    path('private/fhir-search', views_search.fhir_private_search, name="fhir-private-search"),
    path('private/ingest-fhir', views_ingest_fhir.ingest_fhir, name="ingest-fhir"),
    path('private/search', views_search.chord_private_search, name="private-search"),
    path('private/tables/<str:table_id>/search', views_search.chord_private_table_search, name="private-table-search"),
] + ([path('admin/', admin.site.urls)] if DEBUG else [])
