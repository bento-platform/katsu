__all__ = [
    "PROP_LABEL",
    "PROP_CITY",
    "PROP_COUNTRY",
    "PROP_ISO3166_ALPHA_3",
    "PROP_PRECISION",
    "GEO_LOCATION",
]

PROP_LABEL = "Address or other human-readable location name."
PROP_CITY = "Optional name of the city where this location rests."
PROP_COUNTRY = "Optional name of the country where this location rests."
PROP_ISO3166_ALPHA_3 = "Optional ISO 3166-1 alpha 3 country code (three letters)."
PROP_PRECISION = 'Optional, human-readable indication of how precise this location is (e.g., "city").'

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
                "schema block."
            ),
            "properties": {
                "label": PROP_LABEL,
                "city": PROP_CITY,
                "country": PROP_COUNTRY,
                "ISO3166alpha3": PROP_ISO3166_ALPHA_3,
                "precision": PROP_PRECISION,
            },
        },
    },
}
