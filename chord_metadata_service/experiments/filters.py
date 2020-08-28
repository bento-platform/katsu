import django_filters
from . import models as m


class ExperimentFilter(django_filters.rest_framework.FilterSet):
    experiment_type = django_filters.CharFilter(lookup_expr='iexact')
    molecule = django_filters.CharFilter(lookup_expr='iexact')
    library_strategy = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = m.Experiment
        fields = ["id", "reference_registry_id",
                  "experiment_type", "molecule",
                  "library_strategy", "biosample"]
