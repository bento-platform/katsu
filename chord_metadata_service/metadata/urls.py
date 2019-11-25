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
from chord_metadata_service.restapi import api_views, urls as restapi_urls
from chord_metadata_service.chord import views_ingest, views_search
from rest_framework.schemas import get_schema_view

from .settings import DEBUG


urlpatterns = [
    path('', get_schema_view(
        title="Metadata Service API",
        description="Metadata Service provides a phenotypic description of an Individual "
        "in the context of biomedical research.",
        version="0.1"
        ),
        name='openapi-schema'),

    path('api/', include(restapi_urls)),
    path('service-info', api_views.service_info),

    path('workflows', views_ingest.workflow_list),
    path('workflows/<slug:workflow_id>', views_ingest.workflow_item),
    path('workflows/<slug:workflow_id>.wdl', views_ingest.workflow_file),

    path('ingest', views_ingest.ingest),

    path('data-types', views_search.data_type_list, name="data-type-list"),
    path('data-types/phenopacket', views_search.data_type_phenopacket, name="data-type-detail"),
    path('data-types/phenopacket/schema', views_search.data_type_phenopacket_schema, name="data-type-schema"),
    # TODO: Consistent snake or kebab
    path('data-types/phenopacket/metadata_schema', views_search.data_type_phenopacket_metadata_schema,
         name="data-type-metadata-schema"),
    path('datasets', views_search.dataset_list, name="table-list"),
    path('datasets/<str:dataset_id>', views_search.dataset_detail, name="table-detail"),
    path('search', views_search.chord_search),
    path('private/search', views_search.chord_private_search),
    path('private/tables/<str:table_id>/search', views_search.chord_private_table_search),
] + [path('admin/', admin.site.urls)] if DEBUG else []
