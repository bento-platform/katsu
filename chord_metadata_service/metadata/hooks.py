def preprocessing_filter_path(endpoints):
    """
    This function used by drf_spectacular to filter out unwanted endpoints.
    For reference, see
    https://drf-spectacular.readthedocs.io/en/latest/customization.html?highlight=hook#step-7-preprocessing-hooks
    """
    filtered = []
    for (path, path_regex, method, callback) in endpoints:
        # Remove all but DRF API endpoints
        if path.startswith("/api/"):
            filtered.append((path, path_regex, method, callback))
    return filtered
