from django.conf import settings

__all__ = [
    "get_threshold",
    "thresholded_count",
]


def get_threshold(low_counts_censored: bool) -> int:
    """
    Gets the maximum count threshold for hiding censored data (i.e., rounding to 0).
    This is a function to prevent settings errors if not running/importing this file in a Django context.
    """
    return settings.CONFIG_PUBLIC["rules"]["count_threshold"] if low_counts_censored else 0


def thresholded_count(c: int, low_counts_censored: bool) -> int:
    return 0 if c <= get_threshold(low_counts_censored) else c
