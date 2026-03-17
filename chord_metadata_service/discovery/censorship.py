from bento_lib.discovery import (
    DiscoveryConfig,
    DiscoveryConfigRules,
    RULES_NO_PERMISSIONS,
    RULES_FULL_PERMISSIONS,
    DiscoveryEntity,
)
from structlog.stdlib import BoundLogger
from typing import TypeAlias

from chord_metadata_service.authz.types import DataPermissions, DataTypeDiscoveryPermissions
from .constants import NESTED_ENTITIES
from .model_lookups import DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE
from .scope import ValidatedDiscoveryScope
from .types import EntityCountOrBoolResponse, EntityCounts
from .utils import extract_discovery

__all__ = [
    "get_threshold",
    "censor_count",
    "thresholded_count",
    "get_max_query_parameters",
    "get_rules",
    "censor_entity_counts",
    "censor_entity_counts_by_dataset",
    "aggregate_counts_from_censored_by_dataset",
]

# If only we had interfaces...
RulesExtractable: TypeAlias = DiscoveryConfigRules | DiscoveryConfig | ValidatedDiscoveryScope


def get_rules(discovery_or_scope_or_rules: RulesExtractable, data_permissions: DataPermissions) -> DiscoveryConfigRules:
    if data_permissions.data:
        return RULES_FULL_PERMISSIONS
    elif not (data_permissions.counts or data_permissions.bool_):
        return RULES_NO_PERMISSIONS
    # If discovery is "empty", this will most likely be equivalent to RULES_NO_PERMISSIONS:
    return (
        discovery_or_scope_or_rules
        if isinstance(discovery_or_scope_or_rules, DiscoveryConfigRules)
        else extract_discovery(discovery_or_scope_or_rules).rules
    )


def get_threshold(discovery_or_scope_or_rules: RulesExtractable, field_set_permissions: DataPermissions) -> int:
    """
    Gets the maximum count threshold for censoring counts data (i.e., rounding to 0).
    """
    return get_rules(discovery_or_scope_or_rules, field_set_permissions).count_threshold


def censor_count(c: int, t: int) -> int:
    """
    Censors a count if it is less than or equal to a threshold. We make this a tiny little function to ensure
    less-than-or-equal-to is used consistently.
    """
    return 0 if c <= t else c


def thresholded_count(
    c: int,
    discovery_or_scope_or_rules: RulesExtractable,
    field_set_permissions: DataPermissions,
) -> int:
    return censor_count(c, get_threshold(discovery_or_scope_or_rules, field_set_permissions))


def get_max_query_parameters(
    discovery_or_scope_or_rules: RulesExtractable,
    field_set_permissions: DataPermissions,
) -> int:
    """
    Gets the maximum number of query parameters allowed for discovery.
    """
    return get_rules(discovery_or_scope_or_rules, field_set_permissions).max_query_parameters


async def censor_entity_counts(
    discovery_or_scope_or_rules: RulesExtractable,
    counts: EntityCounts,
    dt_permissions: DataTypeDiscoveryPermissions,
    lg: BoundLogger,
) -> EntityCountOrBoolResponse:
    """
    Given a set of counts for discovery entities (presumably matching a particular query/discovery scope)
    Note on nested censorship:
        If a given entity gets censored to a zero-count/False, we need to censor any "nested" entities (e.g., biosamples
        within phenopackets, experiment results within experiments) to prevent what amounts to leaking that we have at
        least one phenopacket.
    """

    # for each 'discovery entity', we generate either:
    #  - a count (0/count-if-above-threshold), or
    #  - a boolean (count > threshold)
    count_or_bools_res: EntityCountOrBoolResponse = {}

    # TODO: permissions non-hard-coded
    for e in counts:
        dt = DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE[e]
        entity_permissions = dt_permissions[dt]
        count_threshold = get_threshold(discovery_or_scope_or_rules, entity_permissions)

        entity_count = counts[e]

        # Extra check for threshold being above 0 to not log warnings for true-0 counts with query:data
        if 0 < counts[e] <= count_threshold and count_threshold > 0:
            await lg.ainfo("discovery: entity count is below threshold", entity=e, threshold=count_threshold)
            entity_count = 0  # censor sub-threshold counts to 0

        if entity_permissions.any_permissions():  # if we have any permissions, then add a response for the overview
            # if we only have boolean permissions, store a Boolean "count" (yes or no to above-threshold count) if we
            # didn't get censored down to 0 above.
            # This key used to be a plural version of the public model name, but is now singular so we have a consistent
            # key to use across all discovery endpoints:
            count_or_bools_res[e] = entity_count if entity_permissions.counts else (entity_count > 0)

    for e in count_or_bools_res:
        if not count_or_bools_res[e] and not dt_permissions[DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE[e]].data:
            for ee in NESTED_ENTITIES[e]:
                ee_perms = dt_permissions[DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE[ee]]
                if ee_perms.data:
                    continue
                count_or_bools_res[ee] = 0 if ee_perms.counts else False

    return count_or_bools_res


async def censor_entity_counts_by_dataset(
    scope: ValidatedDiscoveryScope,
    counts_by_dataset: dict[str, EntityCounts],
    dt_permissions: DataTypeDiscoveryPermissions,
    lg: BoundLogger,
) -> dict[str, EntityCountOrBoolResponse]:

    res: dict[str, EntityCountOrBoolResponse] = {}

    for dataset_id, entity_counts in counts_by_dataset.items():
        censored = await censor_entity_counts(scope, entity_counts, dt_permissions, lg)
        if censored:
            res[dataset_id] = censored

    return res


def aggregate_counts_from_censored_by_dataset(
    counts_by_dataset: dict[str, EntityCountOrBoolResponse],
) -> EntityCountOrBoolResponse:

    all_entities: set[DiscoveryEntity] = set()
    for ds_counts in counts_by_dataset.values():
        all_entities.update(ds_counts.keys())

    aggregated: EntityCountOrBoolResponse = {}
    for entity in all_entities:
        values: list[int | bool] = [
            ds_counts[entity]
            for ds_counts in counts_by_dataset.values()
            if entity in ds_counts
        ]
        # If any dataset-level value is boolean, treat the aggregated value as boolean (OR)
        if any(isinstance(v, bool) for v in values):
            aggregated[entity] = any(bool(v) for v in values)
        else:
            # All numeric: sum them
            aggregated[entity] = sum(int(v) for v in values)

    return aggregated
