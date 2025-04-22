from bento_lib.discovery import DiscoveryConfig, DiscoveryConfigRules, RULES_NO_PERMISSIONS, RULES_FULL_PERMISSIONS
from ..authz.types import DataPermissionsDict

__all__ = [
    "get_threshold",
    "thresholded_count",
    "get_max_query_parameters",
    "get_rules",
]


def get_rules(discovery: DiscoveryConfig, data_permissions: DataPermissionsDict) -> DiscoveryConfigRules:
    if data_permissions["data"]:
        return RULES_FULL_PERMISSIONS
    elif not data_permissions["counts"]:
        return RULES_NO_PERMISSIONS
    return discovery.rules  # If discovery is "empty", this will most likely be equivalent to RULES_NO_PERMISSIONS.


def get_threshold(discovery: DiscoveryConfig, field_set_permissions: DataPermissionsDict) -> int:
    """
    Gets the maximum count threshold for censoring counts data (i.e., rounding to 0).
    """
    return get_rules(discovery, field_set_permissions).count_threshold


def thresholded_count(
    c: int,
    discovery: DiscoveryConfig,
    field_set_permissions: DataPermissionsDict,
) -> int:
    return 0 if c <= get_threshold(discovery, field_set_permissions) else c


def get_max_query_parameters(
    discovery: DiscoveryConfig,
    field_set_permissions: DataPermissionsDict,
) -> int:
    """
    Gets the maximum number of query parameters allowed for discovery.
    """
    return get_rules(discovery, field_set_permissions).max_query_parameters
