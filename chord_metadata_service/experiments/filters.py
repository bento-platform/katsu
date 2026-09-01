import django_filters
from django.db.models import Q

from chord_metadata_service.phenopackets.filters import filter_datasets
from .models import Experiment, ExperimentResult


class ExperimentFilter(django_filters.rest_framework.FilterSet):
    study_type = django_filters.CharFilter(lookup_expr="icontains")
    experiment_type = django_filters.CharFilter(lookup_expr="icontains")
    molecule = django_filters.CharFilter(lookup_expr="icontains")
    library_strategy = django_filters.CharFilter(lookup_expr="icontains")
    library_source = django_filters.CharFilter(lookup_expr="icontains")
    library_selection = django_filters.CharFilter(lookup_expr="icontains")
    library_layout = django_filters.CharFilter(lookup_expr="icontains")
    extraction_protocol = django_filters.CharFilter(lookup_expr="icontains")
    extra_properties = django_filters.CharFilter(method="filter_extra_properties", label="Extra properties")
    # filter by datasets
    datasets = django_filters.CharFilter(method=filter_datasets, field_name="dataset_id", label="Datasets")

    class Meta:
        model = Experiment
        fields = ["id", "reference_registry_id", "biosample"]

    def filter_extra_properties(self, qs, name, value):
        return qs.filter(extra_properties__icontains=value)


class ExperimentResultFilter(django_filters.rest_framework.FilterSet):
    identifier = django_filters.CharFilter(lookup_expr="exact")
    description = django_filters.CharFilter(lookup_expr="icontains")
    filename = django_filters.CharFilter(lookup_expr="icontains")
    url = django_filters.CharFilter(lookup_expr="icontains")
    # special filter used for the experiment_results_drs.wdl association workflow to find experiment results which may
    # be missing a DRS URL or indices
    drs_association_candidate = django_filters.BooleanFilter(
        method="filter_drs_association_candidate", label="DRS association candidate"
    )

    indices = django_filters.CharFilter(method="filter_indices", label="Indices")
    storage_uri = django_filters.CharFilter(lookup_expr="icontains")
    storage_server = django_filters.CharFilter(lookup_expr="icontains")
    genome_assembly_id = django_filters.CharFilter(lookup_expr="iexact")
    file_format = django_filters.CharFilter(lookup_expr="iexact")
    data_output_type = django_filters.CharFilter(lookup_expr="icontains")
    usage = django_filters.CharFilter(lookup_expr="icontains")
    created_by = django_filters.CharFilter(lookup_expr="icontains")
    extra_properties = django_filters.CharFilter(method="filter_extra_properties", label="Extra properties")
    # filter by datasets
    datasets = django_filters.CharFilter(method=filter_datasets, field_name="experiments__dataset_id", label="Datasets")

    class Meta:
        model = ExperimentResult
        exclude = ["creation_date", "created", "updated", "fts_extra"]

    def filter_drs_association_candidate(self, qs, name, value):
        q = Q(url__isnull=True) | Q(file_format__in=("BAM", "CRAM", "VCF", "BCF", "GVCF", "FASTA", "FASTQ"), indices=[])
        if not value:
            q = ~q
        return qs.filter(q)

    def filter_indices(self, qs, name, value):
        return qs.filter(indices__icontains=value)

    def filter_extra_properties(self, qs, name, value):
        return qs.filter(extra_properties__icontains=value)
