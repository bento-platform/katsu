from bento_lib.discovery import DiscoveryConfig, FieldDefinition
from django.db.models import Count, F, QuerySet

from chord_metadata_service.authz.types import DataPermissions

from .censorship import thresholded_count
from .fields_utils import get_jsonb_path_query, MAPPING_SEPARATOR
from .pydantic_models import BinWithValue, BinList

__all__ = [
    "individual_experiment_type_stats",
    "individual_biosample_tissue_stats",
    "bento_public_format_count_and_stats_list",
    "queryset_stats_for_field",
]


async def individual_experiment_type_stats(
    queryset: QuerySet, discovery: DiscoveryConfig, field_permissions: DataPermissions,
) -> tuple[int, BinList]:
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
) -> tuple[int, BinList]:
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
) -> tuple[int, BinList]:
    # only used for legacy stats calculations above

    stats_list: BinList = BinList(root=[])
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
            stats_list.append(BinWithValue(key=label, label=label, value=thresholded_value))

    return thresholded_count(total, discovery, field_permissions), stats_list


def _queryset_key_and_values_for_field(
    queryset: QuerySet, field: str, group_by: str | None, is_ontology_class: bool
) -> tuple[str, str | None, QuerySet]:
    """
    Helper function to rename the field we want (if possibly nested) to something that won't conflict with a real key on
    the queryset, especially if we're digging into some JSONB object.
    """

    # to prevent a JSONB path query from conflicting with a potentially real key on the queryset, we cannot use just the
    # field access path as a unique ID - we can include the group_by clause as well (and add a prefix) to prevent a
    # collision, e.g.:
    #  with mapping=individual/phenopackets/medical_actions, group_by=procedure/code/label, just using mapping (field)
    #  as the unique key would collide with the real medical_actions field on phenopackets after we normalize mapping.
    #  By instead using _jsonb_medical_actions_procedure_code_label as the annotation key, we have something unique.
    queryset_key = (
        f"_jsonb_{field}_{(group_by + '/id').replace(MAPPING_SEPARATOR, '_')}"
        if group_by is not None else f"{field}{"__id" if is_ontology_class else ""}"
    )
    queryset_label_key: str | None = (
        f"_jsonb_{field}_{(group_by + '/label').replace(MAPPING_SEPARATOR, '_')}"
        if group_by is not None else f"{field}__label"
    ) if is_ontology_class else None

    # values() restrict the table of results to this COLUMN
    if group_by is not None:
        return (
            queryset_key,
            queryset_label_key,
            queryset.values(**{queryset_key: get_jsonb_path_query(field, group_by)}),
        )
    else:
        return (
            queryset_key,
            queryset_label_key,
            queryset.values(*((queryset_key, queryset_label_key) if queryset_label_key else (queryset_key,))),
        )


async def queryset_stats_for_field(
    queryset: QuerySet,
    field: str,
    field_props: FieldDefinition,
    discovery: DiscoveryConfig | None,
    field_permissions: DataPermissions | None,
    add_missing: bool = False,
    should_censor: bool = True,
) -> dict[str, tuple[str, int]]:
    """
    Computes counts of distinct values for a queryset and a given field. Mainly applicable to
    fields representing categorical values.
    :return: dictionary of [key, (label, count)]
    """

    if (discovery is None or field_permissions is None) and should_censor:
        raise Exception("cannot censor without discovery config")

    queryset_key, queryset_label_key, queryset_values = _queryset_key_and_values_for_field(
        queryset,
        field,
        field_props.group_by,
        is_ontology_class=field_props.datatype == "ontology-class"
    )

    # annotate() creates a `total` column for the aggregation
    # Count("*") aggregates results including nulls
    # this empty order_by() clears any previous ordering set, which can interfere with annotations
    #  - see https://docs.djangoproject.com/en/5.2/topics/db/aggregation/#interaction-with-order-by
    annotated_queryset = queryset_values.annotate(total=Count("*")).order_by()
    num_missing = 0

    stats: dict[str, tuple[str, int]] = {}

    async for item in annotated_queryset:
        key = item[queryset_key]
        if key is None:
            num_missing = item["total"]
            continue

        key = str(key) if not isinstance(key, str) else key.strip()
        if key == "":
            continue

        # Censor low cell counts if necessary - we don't want to betray that the value even exists in the database if
        # we have a low count for it.
        if should_censor and thresholded_count(item["total"], discovery, field_permissions) == 0:
            continue

        label = str(item[queryset_label_key]).strip() if queryset_label_key is not None else key
        stats[key] = (label, item["total"])

    # Sort statistics dictionary in order of lowercase label
    stats = dict(sorted(stats.items(), key=lambda s: s[1][0].lower()))

    if add_missing:
        stats["missing"] = (
            "missing",
            thresholded_count(num_missing, discovery, field_permissions) if should_censor else num_missing
        )

    return stats
