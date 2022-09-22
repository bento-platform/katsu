import django_filters
import logging

logger = logging.getLogger(__name__)

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


# TODO   authorize_datasets(): remove the code == GRU filter, urgently.
def authorize_datasets(qs, name, value):
    """
    Filter by authorized datasets.
    If value is 'NO_DATASETS_AUTHORIZED', returns no objects.
    Otherwise, returns objects that are in the specified datasets.
    """
    logger.warn(f"value is {value}")
    if value == "NO_DATASETS_AUTHORIZED":
        lookup = "__".join([name, "in"])
        return qs.filter(**{lookup: []})
    else:
        lookup = "__".join([name, "in"])

        # TODO  THE FILTER BELOW IS JANKY; NEEDS TO BE REMOVED.
        #       It is only here for the ClinDIG 4.3 demo.
        temp = qs.filter(**{lookup: value.split(",")}).distinct()\
            .filter(data_use__consent_code__primary_category__code='GRU')
        for t in temp:
            logger.warn(str(t.data_use))

        return temp


class AuthorizedDatasetFilter(django_filters.rest_framework.FilterSet):
    datasets = django_filters.CharFilter(
        method=filter_datasets, field_name="table_ownership__dataset__title",
        label="Datasets"
    )
    authorized_datasets = django_filters.CharFilter(
        method=authorize_datasets, field_name="table_ownership__dataset__title",
        label="Authorized datasets"
    )
