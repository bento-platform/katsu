from django.db.models import Count, F, Model, QuerySet

from typing import Mapping, Type

from .utils import ValidatedDiscoveryScope, get_public_model_scoped_queryset
from ..authz.types import DataPermissionsDict

from .censorship import thresholded_count
from .fields_utils import get_jsonb_path_query, get_public_model_name
from .types import BinWithValue, DiscoveryConfig

__all__ = [
    "individual_experiment_type_stats",
    "individual_biosample_tissue_stats",
    "bento_public_format_count_and_stats_list",
    "stats_for_field",
    "queryset_stats_for_field",
    "get_scoped_queryset",
]


async def individual_experiment_type_stats(
    queryset: QuerySet, discovery: DiscoveryConfig, field_permissions: DataPermissionsDict,
) -> tuple[int, list[BinWithValue]]:
    """
    Used for a fixed-response public API and beacon.
    returns count and bento_public format list of stats for experiment type
    note that queryset_stats_for_field() does not count "missing" correctly when the field has multiple foreign keys
    """
    return await bento_public_format_count_and_stats_list(
        queryset
        .values(label=F("phenopackets__biosamples__experiment__experiment_type"))
        .annotate(value=Count("phenopackets__biosamples__experiment", distinct=True)),
        discovery,
        field_permissions,
    )


async def individual_biosample_tissue_stats(
    queryset: QuerySet, discovery: DiscoveryConfig | None, field_permissions: DataPermissionsDict
) -> tuple[int, list[BinWithValue]]:
    """
    Used for a fixed-response public API and beacon.
    returns count and bento_public format list of stats for biosample sampled_tissue
    """
    return await bento_public_format_count_and_stats_list(
        queryset
        .values(label=F("phenopackets__biosamples__sampled_tissue__label"))
        .annotate(value=Count("phenopackets__biosamples", distinct=True)),
        discovery,
        field_permissions,
    )


async def bento_public_format_count_and_stats_list(
    annotated_queryset: QuerySet,
    discovery: DiscoveryConfig | None,
    field_permissions: DataPermissionsDict,
) -> tuple[int, list[BinWithValue]]:
    stats_list: list[BinWithValue] = []
    total: int = 0

    # TODO: improve censorship tests for search/beacon counts/stats
    async for q in annotated_queryset:
        label = q["label"]
        raw_value = int(q["value"])
        thresholded_value = thresholded_count(raw_value, discovery, field_permissions)

        # increment with raw count for accurate total
        total += raw_value

        # Be careful not to leak values if they're in the database but below threshold
        if label is not None and thresholded_value > 0:
            stats_list.append({"label": label, "value": thresholded_value})

    return thresholded_count(total, discovery, field_permissions), stats_list


def get_scoped_queryset(model: Type[Model], discovery_scope: ValidatedDiscoveryScope) -> QuerySet:
    return get_public_model_scoped_queryset(discovery_scope, get_public_model_name(model))


async def stats_for_field(
    model: Type[Model],
    scope: ValidatedDiscoveryScope,
    field: str,
    field_permissions: DataPermissionsDict,
    add_missing: bool = False,
    group_by: str | None = None,
) -> Mapping[str, int]:
    """
    Computes counts of distinct values for a given field. Mainly applicable to
    char fields representing categories
    """
    qs = get_scoped_queryset(model, scope)
    return await queryset_stats_for_field(
        qs, field, scope.discovery, field_permissions, add_missing=add_missing, group_by=group_by)


async def queryset_stats_for_field(
    queryset: QuerySet,
    field: str,
    discovery: DiscoveryConfig | None,
    field_permissions: DataPermissionsDict,
    add_missing: bool = False,
    group_by: str | None = None
) -> Mapping[str, int]:
    """
    Computes counts of distinct values for a queryset.
    """

    # values() restrict the table of results to this COLUMN
    # annotate() creates a `total` column for the aggregation
    # Count("*") aggregates results including nulls
    if group_by is not None:
        queryset_values = queryset.values(
            **{field: get_jsonb_path_query(field, group_by)},
        )
    else:
        queryset_values = queryset.values(field)
    annotated_queryset = queryset_values.annotate(total=Count("*"))
    num_missing = 0

    stats: dict[str, int] = {}

    async for item in annotated_queryset:
        key = item[field]
        if key is None:
            num_missing = item["total"]
            continue

        key = str(key) if not isinstance(key, str) else key.strip()
        if key == "":
            continue

        # Censor low cell counts if necessary - we don't want to betray that the value even exists in the database if
        # we have a low count for it.
        if thresholded_count(item["total"], discovery, field_permissions) == 0:
            continue

        stats[key] = item["total"]

    if add_missing:
        stats["missing"] = thresholded_count(num_missing, discovery, field_permissions)

    return stats
