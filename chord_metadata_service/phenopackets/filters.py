import django_filters
from django.db.models import Q

from . import models as m


# HELPERS

def filter_ontology(qs, name, value):
    """
    Filters Ontology by id or label
    """
    lookup_id = "__".join([name, "id", "icontains"])
    lookup_label = "__".join([name, "label", "icontains"])
    return qs.filter(Q(**{lookup_id: value}) |
                     Q(**{lookup_label: value}))


def filter_extra_properties_datatype(qs, name, value):
    """
    If there is "datatype" key in "extra_properties" field the filter will filter by value of this key
    If there is no "datatype" key in "extra_properties" returns 0 results
    """
    lookup = "__".join([name, "datatype", "icontains"])
    return qs.filter(**{lookup: value})


def filter_extra_properties(qs, name, value):
    """
    Filters by a value in extra_properties object; looks for a match in keys and values
    """
    return qs.filter(extra_properties__icontains=value)


def filter_datasets(qs, name, value):
    """
    Filters by datasets.

    If value is None, returns all objects regardless of datasets.
    Otherwise, return objects that are in the specified datasets.
    """
    if value:
        lookup = "__".join([name, "in"])
        return qs.filter(**{lookup: value.split(',')}).distinct()
    else:
        return qs


def filter_time_element(qs, name, value):
    # TODO: better filters
    lookup = "__".join([name, "icontains"])
    return qs.filter(**{lookup: value})


# FILTERS


class BiosampleFilter(django_filters.rest_framework.FilterSet):
    description = django_filters.CharFilter(lookup_expr="icontains")
    sampled_tissue = django_filters.CharFilter(
        method=filter_ontology, field_name="sampled_tissue", label="Sampled tissue"
    )
    taxonomy = django_filters.CharFilter(
        method=filter_ontology, field_name="taxonomy", label="Taxonomy")
    histological_diagnosis = django_filters.CharFilter(
        method=filter_ontology, field_name="histological_diagnosis", label="Histological diagnosis")
    tumor_progression = django_filters.CharFilter(
        method=filter_ontology, field_name="tumor_progression", label="Tumor progression")
    tumor_grade = django_filters.CharFilter(
        method=filter_ontology, field_name="tumor_grade", label="Tumor grade")
    extra_properties = django_filters.CharFilter(method=filter_extra_properties, label="Extra properties")
    datasets = django_filters.CharFilter(
        method=filter_datasets,
        field_name="phenopacket__dataset__title",
        label="Datasets"
    )
    procedure = django_filters.CharFilter(
        method=filter_time_element, field_name="procedure", label="Procedure")

    class Meta:
        model = m.Biosample
        fields = ["id", "individual", "is_control_sample"]


class PhenopacketFilter(django_filters.rest_framework.FilterSet):
    disease = django_filters.CharFilter(
        method=filter_ontology, field_name="diseases__term", label="Disease"
    )
    found_phenotypic_feature = django_filters.CharFilter(
        method="filter_found_phenotypic_feature", field_name="phenotypic_features",
        label="Found phenotypic feature"
    )
    extra_properties = django_filters.CharFilter(method=filter_extra_properties, label="Extra properties")
    datasets = django_filters.CharFilter(
        method=filter_datasets,
        field_name="dataset__title",
        label="Datasets"
    )

    class Meta:
        model = m.Phenopacket
        fields = ["id", "subject"]

    def filter_found_phenotypic_feature(self, qs, name, value):
        """
        Filters only found (present in a patient) Phenotypic features by id or label
        """
        qs = qs.filter(
            Q(phenotypic_features__pftype__id__icontains=value) |
            Q(phenotypic_features__pftype__label__icontains=value),
            phenotypic_features__excluded=False
        ).distinct()
        return qs
