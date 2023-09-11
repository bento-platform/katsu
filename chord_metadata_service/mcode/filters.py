import django_filters


# HELPERS


def filter_datasets(qs, name, value):
    """
    Filters by datasets.
    If value is None, returns all objects regardless of datasets.
    Otherwise, return objects that are in the specified datasets.
    """
    if value:
        lookup = "__".join([name, "in"])
        return qs.filter(**{lookup: value.split(",")}).distinct()
    else:
        return qs


def authorize_datasets(qs, name, value):
    """
    Filter by authorized datasets.
    If value is 'NO_DATASETS_AUTHORIZED', returns no objects.
    Otherwise, returns objects that are in the specified datasets.
    """
    if value == "NO_DATASETS_AUTHORIZED":
        lookup = "__".join([name, "in"])
        return qs.filter(**{lookup: []})
    else:
        lookup = "__".join([name, "in"])
        return qs.filter(**{lookup: value.split(",")}).distinct()


# FITLERS


class GeneticSpecimenFilter(django_filters.rest_framework.FilterSet):
    datasets = django_filters.CharFilter(
        method=filter_datasets,
        field_name="genomicsreport__mcodepacket__dataset__title",
        label="Datasets"
    )
    authorized_datasets = django_filters.CharFilter(
        method=authorize_datasets,
        field_name="genomicsreport__mcodepacket__dataset__title",
        label="Authorized datasets"
    )


class CancerGeneticVariantFilter(django_filters.rest_framework.FilterSet):
    datasets = django_filters.CharFilter(
        method=filter_datasets,
        field_name="genomicsreport__mcodepacket__dataset__title",
        label="Datasets"
    )
    authorized_datasets = django_filters.CharFilter(
        method=authorize_datasets,
        field_name="genomicsreport__mcodepacket__dataset__title",
        label="Authorized datasets"
    )


class GenomicRegionStudiedFilter(django_filters.rest_framework.FilterSet):
    datasets = django_filters.CharFilter(
        method=filter_datasets,
        field_name="genomicsreport__mcodepacket__dataset__title",
        label="Datasets"
    )
    authorized_datasets = django_filters.CharFilter(
        method=authorize_datasets,
        field_name="genomicsreport__mcodepacket__dataset__title",
        label="Authorized datasets"
    )


class GenomicsReportFilter(django_filters.rest_framework.FilterSet):
    datasets = django_filters.CharFilter(
        method=filter_datasets,
        field_name="mcodepacket__dataset__title",
        label="Datasets"
    )
    authorized_datasets = django_filters.CharFilter(
        method=authorize_datasets,
        field_name="mcodepacket__dataset__title",
        label="Authorized datasets"
    )


class LabsVitalFilter(django_filters.rest_framework.FilterSet):
    datasets = django_filters.CharFilter(
        method=filter_datasets,
        field_name="individual__mcodepacket__dataset__title",
        label="Datasets"
    )
    authorized_datasets = django_filters.CharFilter(
        method=authorize_datasets,
        field_name="individual__mcodepacket__dataset__title",
        label="Authorized datasets"
    )


class CancerConditionFilter(django_filters.rest_framework.FilterSet):
    datasets = django_filters.CharFilter(
        method=filter_datasets,
        field_name="mcodepacket__dataset__title",
        label="Datasets"
    )
    authorized_datasets = django_filters.CharFilter(
        method=authorize_datasets,
        field_name="mcodepacket__dataset__title",
        label="Authorized datasets"
    )


class TNMStagingFilter(django_filters.rest_framework.FilterSet):
    datasets = django_filters.CharFilter(
        method=filter_datasets,
        field_name="cancer_condition_id__mcodepacket__dataset__title",
        label="Datasets"
    )
    authorized_datasets = django_filters.CharFilter(
        method=authorize_datasets,
        field_name="cancer_condition_id__mcodepacket__dataset__title",
        label="Authorized datasets"
    )


class CancerRelatedProcedureFilter(django_filters.rest_framework.FilterSet):
    datasets = django_filters.CharFilter(
        method=filter_datasets,
        field_name="mcodepacket__dataset__title",
        label="Datasets"
    )
    authorized_datasets = django_filters.CharFilter(
        method=authorize_datasets,
        field_name="mcodepacket__dataset__title",
        label="Authorized datasets"
    )


class MedicationStatementFilter(django_filters.rest_framework.FilterSet):
    datasets = django_filters.CharFilter(
        method=filter_datasets,
        field_name="mcodepacket__dataset__title",
        label="Datasets"
    )
    authorized_datasets = django_filters.CharFilter(
        method=authorize_datasets,
        field_name="mcodepacket__dataset__title",
        label="Authorized datasets"
    )


class MCodePacketFilter(django_filters.rest_framework.FilterSet):
    datasets = django_filters.CharFilter(
        method=filter_datasets, field_name="dataset__title",
        label="Datasets"
    )
    authorized_datasets = django_filters.CharFilter(
        method=authorize_datasets, field_name="dataset__title",
        label="Authorized datasets"
    )
