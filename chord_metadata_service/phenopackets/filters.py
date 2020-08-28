import django_filters
from . import models as m


class MetaDataFilter(django_filters.rest_framework.FilterSet):
    created_by = django_filters.CharFilter(lookup_expr='icontains')
    submitted_by = django_filters.CharFilter(lookup_expr='icontains')
    phenopacket_schema_version = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = m.MetaData
        fields = ["id", "created_by", "submitted_by", "phenopacket_schema_version"]


class PhenotypicFeatureFilter(django_filters.rest_framework.FilterSet):
    description = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = m.PhenotypicFeature
        fields = ["id", "description", "negated", "biosample", "phenopacket"]


class ProcedureFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = m.Procedure
        fields = ["id"]


class HtsFileFilter(django_filters.rest_framework.FilterSet):
    uri = django_filters.CharFilter(lookup_expr='exact')
    description = django_filters.CharFilter(lookup_expr='icontains')
    hts_format = django_filters.CharFilter(lookup_expr='iexact')
    genome_assembly = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = m.HtsFile
        fields = ["uri", "description", "hts_format", "genome_assembly"]


class GeneFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = m.Gene
        fields = ["id", "symbol"]


class VariantFilter(django_filters.rest_framework.FilterSet):
    allele_type = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = m.Variant
        fields = ["id", "allele_type"]


class DiseaseFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = m.Disease
        fields = ["id"]


class BiosampleFilter(django_filters.rest_framework.FilterSet):
    description = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = m.Biosample
        fields = ["id", "description", "individual", "procedure", "is_control_sample"]


class PhenopacketFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = m.Phenopacket
        fields = ["id", "subject"]


class GenomicInterpretationFilter(django_filters.rest_framework.FilterSet):
    status = django_filters.CharFilter(lookup_expr='iexact')

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
