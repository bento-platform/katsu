import django_filters
from chord_metadata_service.phenopackets.filters import filter_datasets
from .models import Experiment, ExperimentResult


class ExperimentFilter(django_filters.rest_framework.FilterSet):
    study_type = django_filters.CharFilter(lookup_expr='icontains')
    experiment_type = django_filters.CharFilter(lookup_expr='icontains')
    molecule = django_filters.CharFilter(lookup_expr='icontains')
    library_strategy = django_filters.CharFilter(lookup_expr='icontains')
    library_source = django_filters.CharFilter(lookup_expr='icontains')
    library_selection = django_filters.CharFilter(lookup_expr='icontains')
    library_layout = django_filters.CharFilter(lookup_expr='icontains')
    extraction_protocol = django_filters.CharFilter(lookup_expr='icontains')
    extra_properties = django_filters.CharFilter(method="filter_extra_properties", label="Extra properties")
    # filter by datasets
    datasets = django_filters.CharFilter(
        method=filter_datasets,
        field_name="table__ownership_record__dataset__title",
        label="Datasets"
    )

    class Meta:
        model = Experiment
        fields = ["id", "reference_registry_id", "biosample"]

    def filter_extra_properties(self, qs, name, value):
        return qs.filter(extra_properties__icontains=value)


class ExperimentResultFilter(django_filters.rest_framework.FilterSet):
    identifier = django_filters.CharFilter(lookup_expr='exact')
    description = django_filters.CharFilter(lookup_expr='icontains')
    filename = django_filters.CharFilter(lookup_expr='icontains')
    genome_assembly_id = django_filters.CharFilter(lookup_expr='iexact')
    file_format = django_filters.CharFilter(lookup_expr='iexact')
    data_output_type = django_filters.CharFilter(lookup_expr='icontains')
    usage = django_filters.CharFilter(lookup_expr='icontains')
    created_by = django_filters.CharFilter(lookup_expr='icontains')
    extra_properties = django_filters.CharFilter(method="filter_extra_properties", label="Extra properties")
    # filter by datasets
    datasets = django_filters.CharFilter(
        method=filter_datasets,
        field_name="experiment__table__ownership_record__dataset__title",
        label="Datasets"
    )

    class Meta:
        model = ExperimentResult
        exclude = ["creation_date", "created", "updated"]

    def filter_extra_properties(self, qs, name, value):
        return qs.filter(extra_properties__icontains=value)
