"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from chord_metadata_service.mohpackets import urls as moh_urls


def redirect_to_default(request):
    return HttpResponseRedirect("/v2/docs")


urlpatterns = [
    path("v2/", include(moh_urls)),
    path("", redirect_to_default),  # how do i set default to url v2/api/docs
    # OpenAPI 3 documentation with Swagger UI
    path("v1", SpectacularSwaggerView.as_view(), name="swagger-ui"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += [
        # Debug toolbar
        path("__debug__/", include("debug_toolbar.urls")),
    ]
