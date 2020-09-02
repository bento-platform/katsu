import django_filters
from django.contrib.postgres.fields import ArrayField
from graphene_django_extras.types import DjangoObjectType
from graphene_django_extras import DjangoFilterListField

from chord_metadata_service.patients.models import (
    Individual
)


class IndividualTypeFilter(django_filters.FilterSet):
    # So every "complex" fields will need some special handling
    # such as this ArrayField
    alternate_ids = django_filters.CharFilter(lookup_expr=['icontains'])

    class Meta:
        model = Individual
        fields = [
            'id',
            'alternate_ids',
            'sex',
            'ethnicity'
        ]


class IndividualType(DjangoObjectType):
    class Meta:
        model = Individual
        # Avoiding the more "complex" fields for now
        exclude_fields = [
            'age', 
            'karnofsky', 
            'extra_properties', 
            'taxonomy',
            'comorbid_condition',
            'ecog_performance_status'
        ]
        filterset_class = IndividualTypeFilter
        # Next is the more usual way of filtering with graphene_django
        filter_fields = {
            "id": ("exact",)
        }


class Query:
    individuals = DjangoFilterListField(IndividualType)
