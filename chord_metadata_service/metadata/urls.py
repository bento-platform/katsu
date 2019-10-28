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
from restapi import urls as restapi_urls
from chord_metadata_service.patients import api_views, chord_api_views
from rest_framework.schemas import get_schema_view
from .settings import DEBUG

urlpatterns = [
    path('', get_schema_view(title="Metadata Service API"),
        name='openapi-schema'),
    path('api/', include(restapi_urls)),
    # path('service-info/', api_views.service_info),

    path('workflows/', chord_api_views.workflow_list),
    path('workflows/<slug:workflow_id>', chord_api_views.workflow_item),
    path('workflows/<slug:workflow_id>.wdl', chord_api_views.workflow_file),

    path('ingest/', chord_api_views.ingest),
] + [path('admin/', admin.site.urls)] if DEBUG else []
