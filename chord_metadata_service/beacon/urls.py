from django.urls import path

from . import api_views

app_name = "beacon"

urlpatterns = [
    # open urls
    path("", api_views.info, name="beacon_root"),
    path("info", api_views.info, name="beacon_info"),
    path("service-info", api_views.service_info, name="beacon_service-info"),
    path("configuration", api_views.configuration, name="beacon_configuration"),
    path("map", api_views.map, name="beacon_map"),
    path("entry_types", api_views.entry_types, name="beacon_entry_types"),
    # restricted access urls
    path("filtering_terms", api_views.filtering_terms, name="beacon_filtering_terms"),
    path("individuals", api_views.individuals, name="beacon_individuals"),
    path("g_variants", api_views.g_variants, name="beacon_g_variants"),
    path("biosamples", api_views.biosamples, name="beacon_biosamples"),
    path("runs", api_views.runs, name="beacon_runs"),
    path("runs/<str:entry_id>", api_views.runs, name="beacon_runs_detail"),
    path("analyses", api_views.analyses, name="beacon_analyses"),
    path("analyses/<str:entry_id>", api_views.analyses, name="beacon_analyses_detail"),
    path("cohorts", api_views.cohorts, name="beacon_cohorts"),
    path("cohorts/<str:entry_id>", api_views.cohorts, name="beacon_cohorts_detail"),
    path("datasets", api_views.datasets, name="beacon_datasets"),
    path("datasets/<str:entry_id>", api_views.datasets, name="beacon_datasets_detail"),
]
