import sys

from django.conf import settings

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


def get_threshold(low_counts_censored: bool) -> int:
    """
    Gets the maximum count threshold for hiding censored data (i.e., rounding to 0).
    """
    if not low_counts_censored:
        return 0
    if not settings.CONFIG_PUBLIC:
        return RULES_NO_PERMISSIONS["count_threshold"]
    return settings.CONFIG_PUBLIC["rules"]["count_threshold"]


def thresholded_count(c: int, low_counts_censored: bool) -> int:
    return 0 if c <= get_threshold(low_counts_censored) else c


def get_max_query_parameters(low_counts_censored: bool) -> int:
    """
    Gets the maximum number of query parameters allowed for censored discovery.
    """
    if not low_counts_censored:
        return sys.maxsize
    if not settings.CONFIG_PUBLIC:
        return RULES_NO_PERMISSIONS["max_query_parameters"]
    return settings.CONFIG_PUBLIC["rules"]["max_query_parameters"]
