from bento_lib.discovery import (
    DiscoveryConfig,
    DiscoveryConfigRules,
    RULES_NO_PERMISSIONS,
    RULES_FULL_PERMISSIONS,
)
from chord_metadata_service.authz.types import DataPermissions, DataTypeDiscoveryPermissions
from .constants import NESTED_ENTITIES
from .model_lookups import DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE
from .scope import ValidatedDiscoveryScope
from .types import ModelCountOrBoolResponse
from .utils import extract_discovery

__all__ = [
    "get_threshold",
    "censor_count",
    "thresholded_count",
    "get_max_query_parameters",
    "get_rules",
    "censor_nested_entities",
]


def get_rules(
    discovery_or_scope: DiscoveryConfig | ValidatedDiscoveryScope, data_permissions: DataPermissions
) -> DiscoveryConfigRules:
    if data_permissions.data:
        return RULES_FULL_PERMISSIONS
    elif not (data_permissions.counts or data_permissions.bool_):
        return RULES_NO_PERMISSIONS
    # If discovery is "empty", this will most likely be equivalent to RULES_NO_PERMISSIONS:
    return extract_discovery(discovery_or_scope).rules


def get_threshold(
    discovery_or_scope: DiscoveryConfig | ValidatedDiscoveryScope, field_set_permissions: DataPermissions
) -> int:
    """
    Gets the maximum count threshold for censoring counts data (i.e., rounding to 0).
    """
    return get_rules(discovery_or_scope, field_set_permissions).count_threshold


def censor_count(c: int, t: int) -> int:
    """
    Censors a count if it is less than or equal to a threshold. We make this a tiny little function to ensure
    less-than-or-equal-to is used consistently.
    """
    return 0 if c <= t else c


def thresholded_count(
    c: int,
    discovery_or_scope: DiscoveryConfig | ValidatedDiscoveryScope,
    field_set_permissions: DataPermissions,
) -> int:
    return censor_count(c, get_threshold(discovery_or_scope, field_set_permissions))


def get_max_query_parameters(
    discovery_or_scope: DiscoveryConfig | ValidatedDiscoveryScope,
    field_set_permissions: DataPermissions,
) -> int:
    """
    Gets the maximum number of query parameters allowed for discovery.
    """
    return get_rules(discovery_or_scope, field_set_permissions).max_query_parameters


def censor_nested_entities(
    count_or_bools_res: ModelCountOrBoolResponse, dt_permissions: DataTypeDiscoveryPermissions
) -> None:
    """
    If a given entity gets censored to a zero-count/False, we need to censor any "nested" entities (e.g., biosamples
    within phenopackets, experiment results within experiments) to prevent what amounts to leaking that we have at least
    one phenopacket.
    Side effect: modifies count_or_bools_res to censor these nested entities if needed.
    """
    for e in count_or_bools_res:
        if not count_or_bools_res[e] and not dt_permissions[DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE[e]].data:
            for ee in NESTED_ENTITIES[e]:
                count_or_bools_res[ee] = 0 if dt_permissions[DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE[ee]].counts else False
