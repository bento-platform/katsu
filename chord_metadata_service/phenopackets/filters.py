import django_filters
from . import models as m
from chord_metadata_service.patients.models import Individual
from django_filters.widgets import CSVWidget
from django.db.models import Q


# HELPERS

def filter_ontology(qs, name, value):
    """
    Filters Ontology by id or label
    """
    lookup_id = "__".join([name, "id", "icontains"])
    lookup_label = "__".join([name, "label", "icontains"])
    return qs.filter(Q(**{lookup_id: value}) |
                     Q(**{lookup_label: value}))


def filter_related_model_ids(qs, name, value):
    """
    Returns objects for a list of specified related model ids
    """
    if value:
        lookup = "__".join([name, "in"])
        qs = qs.filter(**{lookup: value})
    return qs


# FILTERS


class MetaDataFilter(django_filters.rest_framework.FilterSet):
    created_by = django_filters.CharFilter(lookup_expr="icontains")
    submitted_by = django_filters.CharFilter(lookup_expr="icontains")
    phenopacket_schema_version = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = m.MetaData
        fields = ["id"]


class PhenotypicFeatureFilter(django_filters.rest_framework.FilterSet):
    description = django_filters.CharFilter(lookup_expr="icontains")
    type = django_filters.CharFilter(method=filter_ontology, field_name="pftype", label="Type")
    severity = django_filters.CharFilter(method=filter_ontology, field_name="severity", label="Severity")
    # TODO modifier
    onset = django_filters.CharFilter(method=filter_ontology, field_name="onset", label="Onset")
    evidence = django_filters.CharFilter(method="filter_evidence", field_name="evidence", label="Evidence")
    # TODO not all projects will have datatype depending on the requirements
    extra_properties_datatype = django_filters.CharFilter(
        method="filter_extra_properties_datatype", field_name="extra_properties",
        label="Extra properties datatype"
    )
    individual = django_filters.ModelMultipleChoiceFilter(
        queryset=Individual.objects.all(), widget=CSVWidget,
        field_name="phenopacket__subject", method=filter_related_model_ids,
        label="Individual"
    )

    class Meta:
        model = m.PhenotypicFeature
        fields = ["id", "negated", "biosample", "phenopacket"]

    def filter_extra_properties_datatype(self, qs, name, value):
        """
        If there is "datatype" key in "extra_properties" field the filter will filter by value of this key
        If there is no "datatype" key in "extra_properties" returns 0 results
        """
        return qs.filter(extra_properties__contains={"datatype": value})

    def filter_evidence(self, qs, name, value):
        """
        Filters Evidence code by both id or label
        """
        return qs.filter(Q(evidence__evidence_code__id__icontains=value) |
                         Q(evidence__evidence_code__label__icontains=value))


class ProcedureFilter(django_filters.rest_framework.FilterSet):
    code = django_filters.CharFilter(method=filter_ontology, field_name="code", label="Code")
    body_site = django_filters.CharFilter(method=filter_ontology, field_name="body_site",label="Body site")
    biosample = django_filters.ModelMultipleChoiceFilter(
        queryset=m.Biosample.objects.all(), widget=CSVWidget, field_name="biosample",
        method=filter_related_model_ids, label="Biosample"
    )

    class Meta:
        model = m.Procedure
        fields = ["id"]


class HtsFileFilter(django_filters.rest_framework.FilterSet):
    description = django_filters.CharFilter(lookup_expr="icontains")
    hts_format = django_filters.CharFilter(lookup_expr="iexact")
    genome_assembly = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = m.HtsFile
        fields = ["uri"]


class GeneFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = m.Gene
        fields = ["id", "symbol"]


class VariantFilter(django_filters.rest_framework.FilterSet):
    allele_type = django_filters.CharFilter(lookup_expr="iexact")
    zygosity = django_filters.CharFilter(method=filter_ontology, field_name="zygosity", label="Zygosity")

    class Meta:
        model = m.Variant
        fields = ["id"]


class DiseaseFilter(django_filters.rest_framework.FilterSet):
    term = django_filters.CharFilter(method=filter_ontology, field_name="term", label="Term")
    # TODO extra_properties 1. datatype 2. comorbidities_group
    # TODO select all patients with disease "Asthma"

    class Meta:
        model = m.Disease
        fields = ["id"]


class BiosampleFilter(django_filters.rest_framework.FilterSet):
    description = django_filters.CharFilter(lookup_expr="icontains")
    sampled_tissue = django_filters.CharFilter(
        method=filter_ontology, field_name="sampled_tissue", label="Sampled tissue"
    )
    taxonomy = django_filters.CharFilter(
        method=filter_ontology, field_name="taxonomy", label="Taxonomy"
    )
    histological_diagnosis = django_filters.CharFilter(
        method=filter_ontology, field_name="histological_diagnosis",
        label="Histological diagnosis"
    )
    # TODO procedure is self.id, how to know procedure id ? filter by term or id
    # TODO rest

    class Meta:
        model = m.Biosample
        fields = ["id", "individual", "procedure", "is_control_sample"]


class PhenopacketFilter(django_filters.rest_framework.FilterSet):
    # TODO filtering by all related objects

    class Meta:
        model = m.Phenopacket
        fields = ["id", "subject"]


class GenomicInterpretationFilter(django_filters.rest_framework.FilterSet):
    status = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = m.GenomicInterpretation
        fields = ["id", "gene", "variant"]


class DiagnosisFilter(django_filters.rest_framework.FilterSet):
    # TODO filtering by disease ontology id or label

    class Meta:
        model = m.Diagnosis
        fields = ["id", "disease"]


class InterpretationFilter(django_filters.rest_framework.FilterSet):
    resolution_status = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = m.Interpretation
        fields = ["id", "phenopacket"]
