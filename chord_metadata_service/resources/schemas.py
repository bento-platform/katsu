from chord_metadata_service.restapi.schemas import EXTRA_PROPERTIES_SCHEMA
from chord_metadata_service.restapi.schema_utils import tag_ids_and_describe

from . import descriptions


__all__ = ["RESOURCE_SCHEMA"]


RESOURCE_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:resources:resource",
    "type": "object",  # TODO
    "properties": {
        "id": {
            "type": "string",
        },
        "name": {
            "type": "string",
        },
        "namespace_prefix": {
            "type": "string",
        },
        "url": {
            "type": "string",
        },
        "version": {
            "type": "string",
        },
        "iri_prefix": {
            "type": "string",
        },
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["id", "name", "namespace_prefix", "url", "version", "iri_prefix"],
}, descriptions.RESOURCE)
