from chord_metadata_service.restapi.schemas import EXTRA_PROPERTIES_SCHEMA
from chord_metadata_service.restapi.schema_utils import tag_ids_and_describe, base_type, SCHEMA_TYPES

from . import descriptions


__all__ = ["RESOURCE_SCHEMA"]


RESOURCE_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:resources:resource",
    "type": "object",
    "properties": {
        "id": base_type(SCHEMA_TYPES.STRING),
        "name": base_type(SCHEMA_TYPES.STRING),
        "namespace_prefix": base_type(SCHEMA_TYPES.STRING),
        "url": base_type(SCHEMA_TYPES.STRING),
        "version": base_type(SCHEMA_TYPES.STRING),
        "iri_prefix": base_type(SCHEMA_TYPES.STRING),
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["id", "name", "namespace_prefix", "url", "version", "iri_prefix"],
}, descriptions.RESOURCE)
