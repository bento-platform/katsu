from pathlib import Path

from chord_metadata_service.restapi.schema_utils import (
    SchemaTypes,
    base_type,
    get_schema_app_id,
    sub_schema_uri,
    tag_ids_and_describe,
)
from chord_metadata_service.restapi.schemas import EXTRA_PROPERTIES_SCHEMA

from . import descriptions

__all__ = ["RESOURCE_SCHEMA"]

base_uri = get_schema_app_id(Path(__file__).parent.name)

RESOURCE_SCHEMA = tag_ids_and_describe(
    {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": sub_schema_uri(base_uri, "resource"),
        "type": "object",
        "properties": {
            "id": base_type(SchemaTypes.STRING),
            "name": base_type(SchemaTypes.STRING),
            "namespace_prefix": base_type(SchemaTypes.STRING),
            "url": base_type(SchemaTypes.STRING),
            "version": base_type(SchemaTypes.STRING),
            "iri_prefix": base_type(SchemaTypes.STRING),
            "extra_properties": EXTRA_PROPERTIES_SCHEMA,
        },
        "required": ["id", "name", "namespace_prefix", "url", "version", "iri_prefix"],
    },
    descriptions.RESOURCE,
)
