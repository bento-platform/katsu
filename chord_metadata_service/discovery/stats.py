from bento_lib.discovery import DiscoveryConfig
from django.db.models import Count, F, QuerySet
from typing import Mapping

from chord_metadata_service.authz.types import DataPermissions

from .censorship import thresholded_count
from .fields_utils import get_jsonb_path_query
from .pydantic_models import BinWithValue

__all__ = [
    "individual_experiment_type_stats",
    "individual_biosample_tissue_stats",
    "bento_public_format_count_and_stats_list",
    "stats_for_field",
    "queryset_stats_for_field",
]


async def individual_experiment_type_stats(
    queryset: QuerySet, discovery: DiscoveryConfig, field_permissions: DataPermissions,
) -> tuple[int, list[BinWithValue]]:
    """
    Used for a fixed-response public API and beacon.
    returns count and bento_public format list of stats for experiment type
    Note: queryset_stats_for_field() does not count "missing" correctly when the field has multiple foreign keys.
    """

    # Note: the queryset used to join through phenopackets, but individuals can be created without a phenopacket (which
    # occurs sometimes in tests or in the case of a new packet model), which would cause this to return the wrong stats.

    return await bento_public_format_count_and_stats_list(
        queryset
        .values(label=F("phenopackets__biosamples__experiments__experiment_type"))
        .annotate(value=Count("phenopackets__biosamples__experiments", distinct=True)),
        discovery,
        field_permissions,
    )


async def individual_biosample_tissue_stats(
    queryset: QuerySet, discovery: DiscoveryConfig, field_permissions: DataPermissions
) -> tuple[int, list[BinWithValue]]:
    """
    Used for a fixed-response public API and beacon.
    returns count and bento_public format list of stats for biosample sampled_tissue
    """

    # Note: the queryset used to join through phenopackets, but individuals can be created without a phenopacket (which
    # occurs sometimes in tests or in the case of a new packet model), which would cause this to return the wrong stats.

    return await bento_public_format_count_and_stats_list(
        queryset
        .values(label=F("phenopackets__biosamples__sampled_tissue__label"))
        .annotate(value=Count("phenopackets__biosamples", distinct=True)),
        discovery,
        field_permissions,
    )


async def bento_public_format_count_and_stats_list(
    annotated_queryset: QuerySet,
    discovery: DiscoveryConfig,
    field_permissions: DataPermissions,
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
            stats_list.append(BinWithValue(label=label, value=thresholded_value))

    return thresholded_count(total, discovery, field_permissions), stats_list


async def stats_for_field(
    qs: QuerySet,
    discovery: DiscoveryConfig,
    field: str,
    field_permissions: DataPermissions,
    add_missing: bool = False,
    group_by: str | None = None,
) -> Mapping[str, int]:
    """
    Computes counts of distinct values for a given field. Mainly applicable to
    char fields representing categories
    """
    return await queryset_stats_for_field(
        qs, field, discovery, field_permissions, add_missing=add_missing, group_by=group_by)


async def queryset_stats_for_field(
    queryset: QuerySet,
    field: str,
    discovery: DiscoveryConfig,
    field_permissions: DataPermissions,
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
