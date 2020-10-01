import django_filters
from . import models as m
from chord_metadata_service.patients.models import Individual
from django_filters.widgets import CSVWidget


# HELPERS

def filter_ontology_id(qs, name, value):
    """
    Filters Ontology class JSONField by ontology term id
    """
    lookup = "__".join([name, "contains"])
    return qs.filter(**{lookup: {"id": value}})


def filter_ontology_label(qs, name, value):
    """
    Filters Ontology class JSONField by ontology label
    """
    lookup = "__".join([name, "contains"])
    return qs.filter(**{lookup: {"label": value}})


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
    type_id = django_filters.CharFilter(
        method=filter_ontology_id, field_name="pftype",
        label="Type ID"
    )
    type_label = django_filters.CharFilter(
        method=filter_ontology_label, field_name="pftype",
        label="Type label"
    )
    severity_id = django_filters.CharFilter(
        method=filter_ontology_id, field_name="severity",
        label="Severity ID"
    )
    severity_label = django_filters.CharFilter(
        method=filter_ontology_label, field_name="severity",
        label="Severity label"
    )
    # TODO modifier
    # TODO onset
    # TODO evidence
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
        fields = ["id", "description", "negated", "biosample", "phenopacket",
                  "extra_properties_datatype", "individual_id"]

    def filter_extra_properties_datatype(self, qs, name, value):
        """
        If there is "datatype" key in "extra_properties" field the filter will filter by value of this key
        If there is no "datatype" key in "extra_properties" returns 0 results
        """
        return qs.filter(extra_properties__contains={"datatype": value})


class ProcedureFilter(django_filters.rest_framework.FilterSet):
    code_id = django_filters.CharFilter(
        method=filter_ontology_id, field_name="code",
        label="Code ID"
    )
    code_label = django_filters.CharFilter(
        method=filter_ontology_label, field_name="code",
        label="Code label"
    )
    body_site_id = django_filters.CharFilter(
        method=filter_ontology_id, field_name="body_site",
        label="Body site ID"
    )
    body_site_label = django_filters.CharFilter(
        method=filter_ontology_label, field_name="body_site",
        label="Body site label"
    )
    biosample_id = django_filters.ModelMultipleChoiceFilter(
        queryset=m.Biosample.objects.all(), widget=CSVWidget,
        field_name="biosample", method=filter_related_model_ids,
        label="Biosample ID"
    )

    class Meta:
        model = m.Procedure
        fields = ["id", "code_id", "code_label", "body_site_id", "body_site_label", "biosample_id"]


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
