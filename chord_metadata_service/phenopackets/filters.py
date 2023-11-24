import django_filters
from django_filters.widgets import CSVWidget
from django.db.models import Q

from chord_metadata_service.patients.models import Individual
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


def filter_related_model_ids(qs, name, value):
    """
    Returns objects for a list of specified related model ids
    """
    if value:
        lookup = "__".join([name, "in"])
        qs = qs.filter(**{lookup: value}).distinct()
    return qs


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


def authorize_datasets(qs, name, value):
    """
    Filter by authorized datasets.

    If value is 'NO_DATASETS_AUTHORIZED', returns no objects.
    Otherwise, returns objects that are in the specified datasets.
    """
    if value == 'NO_DATASETS_AUTHORIZED':
        lookup = "__".join([name, "in"])
        return qs.filter(**{lookup: []})
    else:
        lookup = "__".join([name, "in"])
        return qs.filter(**{lookup: value.split(',')}).distinct()


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


class MetaDataFilter(django_filters.rest_framework.FilterSet):
    created_by = django_filters.CharFilter(lookup_expr="icontains")
    submitted_by = django_filters.CharFilter(lookup_expr="icontains")
    phenopacket_schema_version = django_filters.CharFilter(lookup_expr="iexact")
    extra_properties = django_filters.CharFilter(method=filter_extra_properties, label="Extra properties")
    datasets = django_filters.CharFilter(
        method=filter_datasets, field_name="phenopacket__dataset__title", label="Datasets")
    authorized_datasets = django_filters.CharFilter(
        method=authorize_datasets, field_name="phenopacket__dataset__title",
        label="Authorized datasets"
    )

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
    extra_properties = django_filters.CharFilter(method=filter_extra_properties, label="Extra properties")
    extra_properties_datatype = django_filters.CharFilter(
        method=filter_extra_properties_datatype, field_name="extra_properties",
        label="Extra properties datatype"
    )
    individual = django_filters.ModelMultipleChoiceFilter(
        queryset=Individual.objects.all(), widget=CSVWidget,
        field_name="phenopacket__subject", method=filter_related_model_ids,
        label="Individual"
    )
    datasets = django_filters.CharFilter(
        method=filter_datasets,
        field_name="phenopacket__dataset__title",
        label="Datasets"
    )
    authorized_datasets = django_filters.CharFilter(
        method=authorize_datasets,
        field_name="phenopacket__dataset__title",
        label="Authorized datasets"
    )

    class Meta:
        model = m.PhenotypicFeature
        fields = ["id", "excluded", "biosample", "phenopacket"]

    def filter_evidence(self, qs, name, value):
        """
        Filters Evidence code by both id or label
        """
        return qs.filter(Q(evidence__evidence_code__id__icontains=value) |
                         Q(evidence__evidence_code__label__icontains=value))


class ProcedureFilter(django_filters.rest_framework.FilterSet):
    code = django_filters.CharFilter(method=filter_ontology, field_name="code", label="Code")
    body_site = django_filters.CharFilter(method=filter_ontology, field_name="body_site", label="Body site")
    performed = django_filters.CharFilter(method=filter_time_element, field_name="performed", label="Performed")
    extra_properties = django_filters.CharFilter(method=filter_extra_properties, label="Extra properties")


class DiseaseFilter(django_filters.rest_framework.FilterSet):
    term = django_filters.CharFilter(method=filter_ontology, field_name="term", label="Term")
    extra_properties = django_filters.CharFilter(method=filter_extra_properties, label="Extra properties")
    extra_properties_datatype = django_filters.CharFilter(
        method=filter_extra_properties_datatype, field_name="extra_properties",
        label="Extra properties datatype"
    )
    extra_properties_comorbidities_group = django_filters.CharFilter(
        method="filter_extra_properties_cg", field_name="extra_properties",
        label="Extra properties comorbidities group"
    )
    individual = django_filters.ModelChoiceFilter(
        queryset=Individual.objects.all(), field_name="phenopacket__subject",
        label="Individual"
    )
    datasets = django_filters.CharFilter(
        method=filter_datasets,
        field_name="phenopacket__dataset__title",
        label="Datasets"
    )
    authorized_datasets = django_filters.CharFilter(
        method=authorize_datasets,
        field_name="phenopacket__dataset__title",
        label="Authorized datasets"
    )

    class Meta:
        model = m.Disease
        fields = ["id"]

    def filter_extra_properties_cg(self, qs, name, value):
        return qs.filter(extra_properties__comorbidities_group__icontains=value)


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
    authorized_datasets = django_filters.CharFilter(
        method=authorize_datasets,
        field_name="phenopacket__dataset__title",
        label="Authorized datasets"
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
    authorized_datasets = django_filters.CharFilter(
        method=authorize_datasets,
        field_name="dataset__title",
        label="Authorized datasets"
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


class GenomicInterpretationFilter(django_filters.rest_framework.FilterSet):
    status = django_filters.CharFilter(lookup_expr="iexact")
    gene_filter = django_filters.CharFilter(method="filter_gene", field_name="gene_descriptor",
                                            label="Filter by  GeneDescriptor IDs and symbols")
    variant_filter = django_filters.CharFilter(method="filter_variant", field_name="variant_interpretation",
                                               label="Filter by VariantInterpretation ID and ontologies")
    extra_properties = django_filters.CharFilter(method=filter_extra_properties, label="Extra properties")

    def filter_gene(self, qs, name, value):
        # GeneDescriptor filters
        value_id_filter = Q(gene_descriptor__value_id__icontains=value)
        symbol_filter = Q(gene_descriptor__symbol__icontains=value)
        alt_id_filter = Q(gene_descriptor__alternate_ids__icontains=value)
        alt_symbols_filter = Q(gene_descriptor__alternate_symbols__icontains=value)

        qs = qs.filter(
            value_id_filter | symbol_filter | alt_id_filter | alt_symbols_filter
        ).distinct()
        return qs

    def filter_variant(self, qs, name, value):
        id_filter = Q(variant_interpretation__variation_descriptor__id__icontains=value)
        label_filter = Q(variant_interpretation__variation_descriptor__label__icontains=value)
        pathology_class_filter = Q(variant_interpretation__acmg_pathogenicity_classification__icontains=value)
        therapeutic_actionability_filter = Q(variant_interpretation__therapeutic_actionability__icontains=value)
        qs = qs.filter(
            id_filter | label_filter | pathology_class_filter | therapeutic_actionability_filter
        ).distinct()
        return qs

    class Meta:
        model = m.GenomicInterpretation
        fields = ["id", "gene_descriptor", "variant_interpretation"]


class DiagnosisFilter(django_filters.rest_framework.FilterSet):
    disease_type = django_filters.CharFilter(
        method=filter_ontology, field_name="disease__term", label="Disease type"
    )
    extra_properties = django_filters.CharFilter(method=filter_extra_properties, label="Extra properties")
    datasets = django_filters.CharFilter(
        method=filter_datasets,
        field_name="disease__phenopacket__dataset__title",
        label="Datasets"
    )
    authorized_datasets = django_filters.CharFilter(
        method=authorize_datasets,
        field_name="disease__phenopacket__dataset__title",
        label="Authorized datasets"
    )

    class Meta:
        model = m.Diagnosis
        fields = ["id"]


class InterpretationFilter(django_filters.rest_framework.FilterSet):
    progress_status = django_filters.CharFilter(lookup_expr="iexact")
    extra_properties = django_filters.CharFilter(method=filter_extra_properties, label="Extra properties")
    datasets = django_filters.CharFilter(
        method=filter_datasets,
        field_name="phenopacket__dataset__title",
        label="Datasets"
    )
    authorized_datasets = django_filters.CharFilter(
        method=authorize_datasets,
        field_name="phenopacket__dataset__title",
        label="Authorized datasets"
    )

    class Meta:
        model = m.Interpretation
        fields = ["id", "phenopacket"]

    def filter_diagnosis(self, qs, name, value):
        lookup = "__".join([name, "icontains"])
        qs = qs.filter(**{lookup: value}).distinct()
        return qs
