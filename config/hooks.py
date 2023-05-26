def preprocessing_filter_path(endpoints):
    """
    This function used by drf_spectacular to filter out unwanted endpoints.
    For reference, see
    https://drf-spectacular.readthedocs.io/en/latest/customization.html?highlight=hook#step-7-preprocessing-hooks
    """
    filtered = []
    for path, path_regex, method, callback in endpoints:
        # only include endpoints that start with discovery or authorized
        if path.startswith("/v2/discovery") or path.startswith("/v2/authorized"):
            filtered.append((path, path_regex, method, callback))
    return filtered
