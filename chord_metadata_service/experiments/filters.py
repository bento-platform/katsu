import django_filters
from .models import Experiment


class ExperimentFilter(django_filters.rest_framework.FilterSet):
    study_type = django_filters.CharFilter(lookup_expr='icontains')
    experiment_type = django_filters.CharFilter(lookup_expr='icontains')
    molecule = django_filters.CharFilter(lookup_expr='icontains')
    library_strategy = django_filters.CharFilter(lookup_expr='icontains')
    library_source = django_filters.CharFilter(lookup_expr='icontains')
    library_selection = django_filters.CharFilter(lookup_expr='icontains')
    library_layout = django_filters.CharFilter(lookup_expr='icontains')
    extraction_protocol = django_filters.CharFilter(lookup_expr='icontains')
    extra_properties = django_filters.CharFilter(method="filter_extra_properties", label="Extra properties")

    class Meta:
        model = Experiment
        fields = ["id", "reference_registry_id", "biosample"]

    def filter_extra_properties(self, qs, name, value):
        return qs.filter(extra_properties__icontains=value)
