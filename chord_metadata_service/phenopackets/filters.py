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
        fields = ["id", "created_by", "submitted_by", "phenopacket_schema_version"]


class PhenotypicFeatureFilter(django_filters.rest_framework.FilterSet):
    description = django_filters.CharFilter(lookup_expr="icontains")
    type = django_filters.CharFilter(
        method=filter_ontology, field_name="pftype",
        label="Type"
    )
    severity = django_filters.CharFilter(
        method=filter_ontology, field_name="severity",
        label="Severity"
    )
    # TODO modifier
    onset = django_filters.CharFilter(
        method=filter_ontology, field_name="onset",
        label="Onset"
    )
    evidence = django_filters.CharFilter(
        method="filter_evidence", field_name="evidence",
        label="Evidence"
    )
    # TODO not all projects will have datatype depending on the requirements
    extra_properties_datatype = django_filters.CharFilter(
        method="filter_extra_properties_datatype", field_name="extra_properties",
        label="Extra properties datatype"
    )
    # TODO naming is not consistent individual_id vs phenopacket
    individual_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Individual.objects.all(), widget=CSVWidget,
        field_name="phenopacket__subject", method=filter_related_model_ids,
        label="Individual ID"
    )

    class Meta:
        model = m.PhenotypicFeature
        fields = ["id", "description", "type", "severity", "onset",
                  "evidence", "negated", "biosample", "phenopacket",
                  "extra_properties_datatype", "individual_id"]

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
    code = django_filters.CharFilter(
        method=filter_ontology, field_name="code",
        label="Code"
    )
    body_site = django_filters.CharFilter(
        method=filter_ontology, field_name="body_site",
        label="Body site"
    )
    biosample_id = django_filters.ModelMultipleChoiceFilter(
        queryset=m.Biosample.objects.all(), widget=CSVWidget,
        field_name="biosample", method=filter_related_model_ids,
        label="Biosample ID"
    )

    class Meta:
        model = m.Procedure
        fields = ["id", "code", "body_site", "biosample_id"]


class HtsFileFilter(django_filters.rest_framework.FilterSet):
    uri = django_filters.CharFilter(lookup_expr="exact")
    description = django_filters.CharFilter(lookup_expr="icontains")
    hts_format = django_filters.CharFilter(lookup_expr="iexact")
    genome_assembly = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = m.HtsFile
        fields = ["uri", "description", "hts_format", "genome_assembly"]


class GeneFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = m.Gene
        fields = ["id", "symbol"]


class VariantFilter(django_filters.rest_framework.FilterSet):
    allele_type = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = m.Variant
        fields = ["id", "allele_type"]


class DiseaseFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = m.Disease
        fields = ["id"]


class BiosampleFilter(django_filters.rest_framework.FilterSet):
    description = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = m.Biosample
        fields = ["id", "description", "individual", "procedure", "is_control_sample"]


class PhenopacketFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = m.Phenopacket
        fields = ["id", "subject"]


class GenomicInterpretationFilter(django_filters.rest_framework.FilterSet):
    status = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = m.GenomicInterpretation
        fields = ["id", "status", "gene", "variant"]


class DiagnosisFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = m.Diagnosis
        fields = ["id", "disease"]


class InterpretationFilter(django_filters.rest_framework.FilterSet):
    resolution_status = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = m.Interpretation
        fields = ["id", "resolution_status", "phenopacket"]
