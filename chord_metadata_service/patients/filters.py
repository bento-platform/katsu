import django_filters
from .models import Individual


class IndividualFilter(django_filters.rest_framework.FilterSet):
    id = django_filters.AllValuesMultipleFilter()
    sex = django_filters.CharFilter(lookup_expr='iexact')
    ethnicity = django_filters.CharFilter(lookup_expr='iexact')
    # TODO select all patients with disease "Asthma"

    class Meta:
        model = Individual
        fields = ["id", "sex", "ethnicity"]
