import django_filters
from .models import Experiment


class ExperimentFilter(django_filters.rest_framework.FilterSet):
    experiment_type = django_filters.CharFilter(lookup_expr='icontains')
    molecule = django_filters.CharFilter(lookup_expr='icontains')
    library_strategy = django_filters.CharFilter(lookup_expr='icontains')
    extraction_protocol = django_filters.CharFilter(lookup_expr='icontains')
    file_location = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Experiment
        fields = ["id", "reference_registry_id", "biosample"]
