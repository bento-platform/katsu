from pathlib import Path
from chord_metadata_service.restapi.schema_utils import base_schema_uri, get_schema_base_path, sub_schema_uri

# e.g. PATCH
# {
#   "linked_field_sets": [
#     {
#       "name": "subject IDs",
#       "links": {"phenopacket": ["subject", "id"], "variant": ["sample_id"]}
#     }
#   ]
# }


base_path = get_schema_base_path(Path(__file__).parent.name)
base_uri = base_schema_uri(base_path)

LINKED_FIELD_SETS_SCHEMA = {
    "$id": sub_schema_uri(base_uri, "linked_fields_sets"),
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "minLength": 3},
            "fields": {
                "type": "object",
                "propertyNames": {
                    "pattern": r"^\S+$"  # TODO: synchronize pattern
                },
                "minProperties": 2,
                "additionalProperties": {  # Field specification, array format; e.g. ["biosamples", "[item]", "id"]
                    "type": "array",
                    "items": {"type": "string", "minLength": 1}
                }
            }
        },
        "required": ["name", "fields"],
        "additionalProperties": False
    }
}

EXPORT_SCHEMA = {
    "$id": sub_schema_uri(base_uri, "export"),
    "description": "Export endpoint",
    "type": "object",
    "properties": {
        "object_type": {
            "type": "string",
            "enum": ["project", "dataset", "table"]
        },
        "object_id": {"type": "string"},
        "format": {
            "type": "string",
            "enum": ["cbioportal"]
        },
        "output_path": {"type": "string"}
    },
    "required": ["object_type", "object_id", "format"],
    "additionalProperties": False
}
