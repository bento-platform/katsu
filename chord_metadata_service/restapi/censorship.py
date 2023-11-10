import sys

from django.conf import settings
from typing import TypedDict

__all__ = [
    "get_threshold",
    "thresholded_count",
    "get_max_query_parameters",
    "DiscoveryRules",
]


def get_threshold(low_counts_censored: bool) -> int:
    """
    Gets the maximum count threshold for hiding censored data (i.e., rounding to 0).
    """
    return settings.DISCOVERY_COUNT_THRESHOLD if low_counts_censored else 0


def thresholded_count(c: int, low_counts_censored: bool) -> int:
    return 0 if c <= get_threshold(low_counts_censored) else c


def get_max_query_parameters(low_counts_censored: bool) -> int:
    """
    Gets the maximum number of query parameters allowed for censored discovery.
    """
    return settings.DISCOVERY_MAX_QUERY_PARAMETERS if low_counts_censored else sys.maxsize


class DiscoveryRules(TypedDict):
    max_query_parameters: int
    count_threshold: int
