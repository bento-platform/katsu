import sys

from chord_metadata_service.discovery.types import DiscoveryConfig

__all__ = [
    "RULES_NO_PERMISSIONS",
    "get_threshold",
    "thresholded_count",
    "get_max_query_parameters",
]


RULES_NO_PERMISSIONS = {
    "max_query_parameters": 0,  # default to no query parameters allowed
    "count_threshold": sys.maxsize,  # default to MAXINT count threshold (i.e., no counts can be seen)
}


def get_threshold(discovery: DiscoveryConfig, low_counts_censored: bool) -> int:
    """
    Gets the maximum count threshold for hiding censored data (i.e., rounding to 0).
    """
    if not low_counts_censored:
        return 0
    if not discovery:
        return RULES_NO_PERMISSIONS["count_threshold"]
    return discovery["rules"]["count_threshold"]


def thresholded_count(c: int, discovery: DiscoveryConfig, low_counts_censored: bool) -> int:
    return 0 if c <= get_threshold(discovery, low_counts_censored) else c


def get_max_query_parameters(discovery: DiscoveryConfig, low_counts_censored: bool) -> int:
    """
    Gets the maximum number of query parameters allowed for censored discovery.
    """
    if not low_counts_censored:
        return sys.maxsize
    if not discovery:
        return RULES_NO_PERMISSIONS["max_query_parameters"]
    return discovery["rules"]["max_query_parameters"]
