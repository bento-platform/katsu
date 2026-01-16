from django.conf import settings

from . import constants, descriptions
from chord_metadata_service.restapi.schema_utils import (
    DRAFT_07,
    SchemaTypes,
    base_type,
    enum_of,
    sub_schema_uri,
    tag_ids_and_describe,
)

__all__ = ["GEO_LOCATION_SCHEMA"]

geo_base_uri = f"{settings.SCHEMAS_BASE_URL}/geo"

# JSON schema for a GeoJSON feature describing a location, with additional structure derived / adapted from the
# GA4GH/Progenetix GeoLocation schema block: https://schemablocks.org/schema_pages/Progenetix/GeoLocation/
GEO_LOCATION_SCHEMA = tag_ids_and_describe(
    {
        "$schema": DRAFT_07,
        "$id": sub_schema_uri(geo_base_uri, "geo_location"),
        "type": "object",
        "properties": {
            "type": {
                "const": "Feature",
            },
            "geometry": {
                "type": "object",
                "properties": {
                    "type": {
                        "const": "Point",
                    },
                    "coordinates": {
                        "type": "array",
                        "items": {
                            "type": "number",
                            "format": "float",
                        },
                        "minItems": 2,
                        "maxItems": 3,
                    },
                },
                "required": ["type", "coordinates"],
                "additionalProperties": False,  # Geometry must be just type and coordinates
            },
            "properties": {
                "type": "object",
                "properties": {
                    "label": base_type(SchemaTypes.STRING),
                    "city": base_type(SchemaTypes.STRING),
                    "country": base_type(SchemaTypes.STRING),
                    "ISO3166alpha3": enum_of(constants.ISO_3166_1_ALPHA_3_COUNTRY_CODES),
                    "precision": base_type(SchemaTypes.STRING),
                },
                "additionalProperties": True,  # Explicitly allow "extra properties"
            },
        },
        "required": ["type", "geometry", "properties"],
    },
    descriptions.GEO_LOCATION,
)
