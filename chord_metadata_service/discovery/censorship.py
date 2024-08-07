import sys

from ..authz.types import DataPermissionsDict
from .types import DiscoveryConfig, DiscoveryRules

__all__ = [
    "RULES_NO_PERMISSIONS",
    "get_threshold",
    "thresholded_count",
    "get_max_query_parameters",
    "get_rules",
]


RULES_NO_PERMISSIONS: DiscoveryRules = {
    "max_query_parameters": 0,  # default to no query parameters allowed
    "count_threshold": sys.maxsize,  # default to MAXINT count threshold (i.e., no counts can be seen)
}

RULES_FULL_PERMISSIONS: DiscoveryRules = {
    "max_query_parameters": sys.maxsize,
    "count_threshold": 0,
}


def get_rules(discovery: DiscoveryConfig | None, data_permissions: DataPermissionsDict) -> DiscoveryRules:
    if data_permissions["data"]:
        return RULES_FULL_PERMISSIONS
    elif not data_permissions["counts"] or not (discovery or {}).get("rules"):
        return RULES_NO_PERMISSIONS
    return discovery["rules"]


def get_threshold(discovery: DiscoveryConfig | None, field_set_permissions: DataPermissionsDict) -> int:
    """
    Gets the maximum count threshold for censoring counts data (i.e., rounding to 0).
    """
    return get_rules(discovery, field_set_permissions)["count_threshold"]


def thresholded_count(c: int, discovery: DiscoveryConfig | None, field_set_permissions: DataPermissionsDict) -> int:
    return 0 if c <= get_threshold(discovery, field_set_permissions) else c


def get_max_query_parameters(discovery: DiscoveryConfig | None, field_set_permissions: DataPermissionsDict) -> int:
    """
    Gets the maximum number of query parameters allowed for discovery.
    """
    return get_rules(discovery, field_set_permissions)["max_query_parameters"]
