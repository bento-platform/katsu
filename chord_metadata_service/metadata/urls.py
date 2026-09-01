from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from chord_metadata_service.chord import urls as chord_urls
from chord_metadata_service.restapi import api_views
from chord_metadata_service.restapi import urls as restapi_urls

urlpatterns = [
    path("api/", include(restapi_urls)),
    path("service-info", api_views.service_info, name="service-info"),
    *chord_urls.urlpatterns,
    # OpenAPI 3 documentation with Swagger UI
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("", SpectacularSwaggerView.as_view(), name="swagger-ui"),
]
