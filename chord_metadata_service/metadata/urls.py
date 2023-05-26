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
import os

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from chord_metadata_service.chord import urls as chord_urls
from chord_metadata_service.mohpackets import urls as moh_urls
from chord_metadata_service.restapi import api_views
from chord_metadata_service.restapi import urls as restapi_urls

# TODO: django.conf.settings breaks reverse(), how to import properly?
from .settings import DEBUG

urlpatterns = [
    path("api/", include(restapi_urls)),
    path("service-info", api_views.service_info, name="service-info"),
    *chord_urls.urlpatterns,  # TODO: Use include? can we double up?
    *([path("admin/", admin.site.urls)] if DEBUG else []),
    # OpenAPI 3 documentation with Swagger UI
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("", SpectacularSwaggerView.as_view(), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# Only use CanDIG urls
if os.environ.get("CANDIG") == "TRUE":
    urlpatterns = urlpatterns[4:]
