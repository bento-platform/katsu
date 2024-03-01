import sys

from .config import discovery_config

__all__ = [
    "RULES_NO_PERMISSIONS",
    "RULES_FULL_PERMISSIONS",
    "get_threshold",
    "thresholded_count",
    "get_max_query_parameters",
]


RULES_NO_PERMISSIONS = {
    "max_query_parameters": 0,  # default to no query parameters allowed
    "count_threshold": sys.maxsize,  # default to MAXINT count threshold (i.e., no counts can be seen)
}

RULES_FULL_PERMISSIONS = {
    "max_query_parameters": sys.maxsize,
    "count_threshold": 0,
}


def get_threshold(low_counts_censored: bool) -> int:
    """
    Gets the maximum count threshold for hiding censored data (i.e., rounding to 0).
    """
    if not discovery_config:
        return RULES_NO_PERMISSIONS["count_threshold"]
    return discovery_config["rules"]["count_threshold"] if low_counts_censored else 0


def thresholded_count(c: int, low_counts_censored: bool) -> int:
    return 0 if c <= get_threshold(low_counts_censored) else c


def get_max_query_parameters(low_counts_censored: bool) -> int:
    """
    Gets the maximum number of query parameters allowed for censored discovery.
    """
    if not discovery_config:
        return RULES_NO_PERMISSIONS["max_query_parameters"]
    return discovery_config["rules"]["max_query_parameters"] if low_counts_censored else sys.maxsize
