from django.urls import path

from . import api_views

app_name = "beacon"

urlpatterns = [
    # open urls
    path("info", api_views.info, name="info"),
    path("service-info", api_views.service_info, name="service-info"),
    path("configuration", api_views.configuration, name="configuration"),
    path("map", api_views.map, name="map"),
    path("entry_types", api_views.entry_types, name="entry-types"),
    # restricted access urls
    path("filtering_terms", api_views.filtering_terms, name="filtering-terms"),
    path("individuals", api_views.individuals, name="individuals"),
    path("g_variants", api_views.g_variants, name="g-variants"),
    path("biosamples", api_views.biosamples, name="biosamples"),
    path("runs", api_views.runs, name="runs"),
    path("runs/<str:entry_id>", api_views.runs, name="runs-detail"),
    path("analyses", api_views.analyses, name="analyses"),
    path("analyses/<str:entry_id>", api_views.analyses, name="analyses-detail"),
    path("cohorts", api_views.cohorts, name="cohorts"),
    path("cohorts/<str:entry_id>", api_views.cohorts, name="cohorts-detail"),
    path("datasets", api_views.datasets, name="datasets"),
    path("datasets/<str:entry_id>", api_views.datasets, name="datasets-detail"),
]
