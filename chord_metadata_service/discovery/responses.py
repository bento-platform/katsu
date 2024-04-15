__all__ = [
    "INSUFFICIENT_DATA_AVAILABLE",
    "NO_PUBLIC_DATA_AVAILABLE",
    "NO_PUBLIC_FIELDS_CONFIGURED",
]

# Public response when there is no enough data that passes the project-custom threshold
INSUFFICIENT_DATA_AVAILABLE = {"message": "Insufficient data available."}

# Public response when there is no public data available and config file is not provided
NO_PUBLIC_DATA_AVAILABLE = {"message": "No public data available."}

# Public response when public fields are not configured and config file is not provided
NO_PUBLIC_FIELDS_CONFIGURED = {"message": "No public fields configured."}
