import django_filters
from django.db.models import Q

from chord_metadata_service.discovery.full_text_search import full_text_search_vector
from .models import Individual

GENOMIC_INTERPRETATION_QUERY = "phenopackets__interpretations__diagnosis__genomic_interpretations"
GENE_DESCRIPTOR_QUERY = f"{GENOMIC_INTERPRETATION_QUERY}__gene_descriptor"
VARIANT_INTERPRETATION_QUERY = f"{GENOMIC_INTERPRETATION_QUERY}__variant_interpretation"
VARIATION_DESCRIPTOR_QUERY = f"{VARIANT_INTERPRETATION_QUERY}__variation_descriptor"


class IndividualFilter(django_filters.rest_framework.FilterSet):
    id = django_filters.AllValuesMultipleFilter()
    alternate_ids = django_filters.CharFilter(lookup_expr="icontains")
    sex = django_filters.CharFilter(lookup_expr="iexact")
    karyotypic_sex = django_filters.CharFilter(lookup_expr="iexact")
    disease = django_filters.CharFilter(
        method="filter_disease", field_name="phenopackets__diseases",
        label="Disease")
    # e.g. select all patients who have a symptom "dry cough"
    found_phenotypic_feature = django_filters.CharFilter(
        method="filter_found_phenotypic_feature", field_name="phenopackets__phenotypic_features",
        label="Found phenotypic feature"
    )

    extra_properties = django_filters.CharFilter(method="filter_extra_properties", label="Extra properties")
    # full-text search at api/individuals?search=
    search = django_filters.CharFilter(method="filter_search", label="Search")

    # e.g. date_of_birth_after=1987-01-01&date_of_birth_before=1990-12-31
    date_of_birth = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Individual
        fields = ["id", "alternate_ids", "phenopackets__biosamples", "phenopackets"]

    def filter_found_phenotypic_feature(self, qs, name, value):
        """
        Filters only found (present in a patient) Phenotypic features by id or label
        """
        qs = qs.filter(
            Q(phenopackets__phenotypic_features__pftype__id__icontains=value) |
            Q(phenopackets__phenotypic_features__pftype__label__icontains=value),
            phenopackets__phenotypic_features__excluded=False
        ).distinct()
        return qs

    def filter_disease(self, qs, name, value):
        qs = qs.filter(
            Q(phenopackets__diseases__term__id__icontains=value) |
            Q(phenopackets__diseases__term__label__icontains=value)
        ).distinct()
        return qs

    def filter_extra_properties(self, qs, name, value):
        return qs.filter(extra_properties__icontains=value)

    def filter_search(self, qs, name, value):
        return qs.annotate(search=full_text_search_vector("individual")).filter(search=value).distinct("id")
