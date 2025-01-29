__all__ = ["GEO_LOCATION"]

GEO_LOCATION = {
    "description": "A GeoJSON-compatible object representing a geographic location.",
    "properties": {
        "type": "GeoJSON type. Always set to 'Feature'.",
        "geometry": {
            "description": "GeoJSON point geometry object for the location.",
            "properties": {
                "type": "GeoJSON type. Always set to 'Point'.",
                "coordinates": (
                    "Array of two (longitude, latitude) or three (longitude, latitude, altitude) coordinates "
                    "representing a point."
                ),
            },
        },
        "properties": {
            "description": (
                "Additional properties on the GeoJSON. Partially structured via the GA4GH/Progenetix GeoLocation "
                "schema block.",
            ),
            "properties": {
                "label": "Address or other human-readable location name.",
                "city": "Optional name of the city where this location rests.",
                "country": "Optional name of the country where this location rests.",
                "ISO3166alpha3": "Optional ISO 3166-1 alpha 3 country code (three letters).",
                "precision": "Optional, human-readable indication of how precise this location is (e.g., \"city\")."
            },
        },
    },
}
