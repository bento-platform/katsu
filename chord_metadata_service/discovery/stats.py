from django.db.models import Count, F, Model, QuerySet

from typing import Mapping, Type

from .censorship import thresholded_count
from .types import BinWithValue


async def experiment_type_stats(queryset: QuerySet, low_counts_censored: bool) -> tuple[int, list[BinWithValue]]:
    """
    returns count and bento_public format list of stats for experiment type
    note that queryset_stats_for_field() does not count "missing" correctly when the field has multiple foreign keys
    """
    return await bento_public_format_count_and_stats_list(
        queryset
        .values(label=F("phenopackets__biosamples__experiment__experiment_type"))
        .annotate(value=Count("phenopackets__biosamples__experiment", distinct=True)),
        low_counts_censored,
    )


async def biosample_tissue_stats(queryset: QuerySet, low_counts_censored: bool) -> tuple[int, list[BinWithValue]]:
    """
    returns count and bento_public format list of stats for biosample sampled_tissue
    """
    return await bento_public_format_count_and_stats_list(
        queryset
        .values(label=F("phenopackets__biosamples__sampled_tissue__label"))
        .annotate(value=Count("phenopackets__biosamples", distinct=True)),
        low_counts_censored,
    )


async def bento_public_format_count_and_stats_list(
    annotated_queryset: QuerySet,
    low_counts_censored: bool,
) -> tuple[int, list[BinWithValue]]:
    stats_list: list[BinWithValue] = []
    total: int = 0

    async for q in annotated_queryset:
        label = q["label"]
        value = thresholded_count(int(q["value"]), low_counts_censored)

        # Be careful not to leak values if they're in the database but below threshold
        if value == 0:
            continue

        # Skip 'missing' values
        if label is None:
            continue

        total += value
        stats_list.append({"label": label, "value": value})

    return thresholded_count(total, low_counts_censored), stats_list


async def stats_for_field(
    model: Type[Model],
    field: str,
    low_counts_censored: bool,
    add_missing: bool = False,
) -> Mapping[str, int]:
    """
    Computes counts of distinct values for a given field. Mainly applicable to
    char fields representing categories
    """
    return await queryset_stats_for_field(
        model.objects.all(), field, low_counts_censored=low_counts_censored, add_missing=add_missing)


async def queryset_stats_for_field(
    queryset: QuerySet, field: str, low_counts_censored: bool, add_missing: bool = False
) -> Mapping[str, int]:
    """
    Computes counts of distinct values for a queryset.
    """

    # values() restrict the table of results to this COLUMN
    # annotate() creates a `total` column for the aggregation
    # Count("*") aggregates results including nulls

    annotated_queryset = queryset.values(field).annotate(total=Count("*"))
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
        if item["total"] <= low_counts_censored:
            continue

        stats[key] = item["total"]

    if add_missing:
        stats["missing"] = thresholded_count(num_missing, low_counts_censored)

    return stats
