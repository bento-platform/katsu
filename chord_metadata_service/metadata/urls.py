from django.urls import path, include
from chord_metadata_service.restapi import api_views, urls as restapi_urls
from chord_metadata_service.chord import urls as chord_urls
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("api/", include(restapi_urls)),
    path("service-info", api_views.service_info, name="service-info"),
    # TODO: datasets/datasets_v2 routes are exposed twice — at root level (here, via chord_urls.urlpatterns)
    # and under api/ (via restapi_urls router). Consolidate to api/ only and remove the root-level duplicates.
    *chord_urls.urlpatterns,  # TODO: Use include? can we double up?
    # OpenAPI 3 documentation with Swagger UI
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("", SpectacularSwaggerView.as_view(), name="swagger-ui"),
]
