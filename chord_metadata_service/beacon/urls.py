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
    path("filtering_terms/<str:entry_id>", api_views.filtering_terms, name="filtering-terms-detail"),
    path("individuals", api_views.individuals, name="individuals"),
    path("individuals/<str:entry_id>/biosamples", api_views.individual_biosamples, name="individual-biosamples"),
    path("individuals/<str:entry_id>", api_views.individuals, name="individuals-detail"),
    path("g_variants", api_views.g_variants, name="g-variants"),
    path("g_variants/<str:entry_id>/biosamples", api_views.g_variant_biosamples, name="g-variant-biosamples"),
    path("g_variants/<str:entry_id>/individuals", api_views.g_variant_individuals, name="g-variant-individuals"),
    path("g_variants/<str:entry_id>", api_views.g_variants, name="g-variants-detail"),
    path("biosamples", api_views.biosamples, name="biosamples"),
    path("biosamples/<str:entry_id>/runs", api_views.biosample_runs, name="biosample-runs"),
    path("biosamples/<str:entry_id>/analyses", api_views.biosample_analyses, name="biosample-analyses"),
    path("biosamples/<str:entry_id>", api_views.biosamples, name="biosamples-detail"),
    path("runs", api_views.runs, name="runs"),
    path("runs/<str:entry_id>", api_views.runs, name="runs-detail"),
    path("analyses", api_views.analyses, name="analyses"),
    path("analyses/<str:entry_id>", api_views.analyses, name="analyses-detail"),
    path("cohorts", api_views.cohorts, name="cohorts"),
    path("cohorts/<str:entry_id>", api_views.cohorts, name="cohorts-detail"),
    path("datasets", api_views.datasets, name="datasets"),
    path("datasets/<str:entry_id>", api_views.datasets, name="datasets-detail"),
]
