from pathlib import Path
from chord_metadata_service.restapi.schema_utils import (
    get_schema_app_id, sub_schema_uri, array_of, base_type, SchemaTypes, enum_of
)

# e.g. PATCH
# {
#   "linked_field_sets": [
#     {
#       "name": "subject IDs",
#       "links": {"phenopacket": ["subject", "id"], "variant": ["sample_id"]}
#     }
#   ]
# }


base_uri = get_schema_app_id(Path(__file__).parent.name)

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

DISCOVERY_FIELD_SCHEMA = {
    "$id": sub_schema_uri(base_uri, "discovery_named_fields"),
    "description": "Field configuration",
    "type": "object",
    "properties": {
        "mapping": base_type(SchemaTypes.STRING),
        "mapping_for_search_filter": base_type(SchemaTypes.STRING),
        "title": base_type(SchemaTypes.STRING),
        "description": base_type(SchemaTypes.STRING),
        "datatype": enum_of(["number", "string"]),
        "config": {
            "type": "object",
            "properties": {
                # datatype == string
                "enum": array_of(base_type(SchemaTypes.STRING)),
                # datatype == number
                "bins": array_of(base_type(SchemaTypes.NUMBER)),
                "bin_size": base_type(SchemaTypes.NUMBER),
                "taper_left": base_type(SchemaTypes.NUMBER),
                "taper_right": base_type(SchemaTypes.NUMBER),
                "units": base_type(SchemaTypes.STRING),
                "minimum": base_type(SchemaTypes.NUMBER),
                "maximum": base_type(SchemaTypes.NUMBER),
                # JSONField array specific
                "group_by": base_type(SchemaTypes.STRING),
                "group_by_value": base_type(SchemaTypes.STRING),
                "value_mapping": base_type(SchemaTypes.STRING),
            }
        }
    },
    "additionalProperties": False
}

DISCOVERY_NAMED_FIELDS_SCHEMA = {
    "$id": sub_schema_uri(base_uri, "discovery_named_fields"),
    "description": "Intermediate schema, enforces field schema with flexible names.",
    "type": "object",
    "patternProperties": {
        "^.*$": { DISCOVERY_FIELD_SCHEMA }
    },
    "additionalProperties": False
}

DISCOVERY_OVERVIEW_CHART_SCHEMA = {
    "$id": sub_schema_uri(base_uri, "discovery_overview_chart"),
    "description": "Associates a field name with a chart type for overview display",
    "type": "object",
    "properties": {
        "field": base_type(SchemaTypes.STRING),
        "chart_type": enum_of(["bar", "pie"])
    },
    "additionalProperties": False
}

DISCOVERY_OVERVIEW_SCHEMA = {
    "$id": sub_schema_uri(base_uri, "discovery_overview"),
    "description": "An overview section containing charts",
    "type": "object",
    "properties": {
        "section_title": base_type(SchemaTypes.STRING),
        "charts": array_of(DISCOVERY_OVERVIEW_CHART_SCHEMA)
    },
    "additionalProperties": False
}

DISCOVERY_SCHEMA = {
    "$id": sub_schema_uri(base_uri, "discovery"),
    "description": "Discovery configuration for public fields/search",
    "type": "object",
    "properties": {
        "overview": array_of(DISCOVERY_OVERVIEW_SCHEMA, "List of overview sections"),
        "search": array_of(),
        "fields": DISCOVERY_NAMED_FIELDS_SCHEMA,
        "rules": {
            "type": "object",
            "properties": {
                "count_threshold": base_type(SchemaTypes.INTEGER),
                "max_query_parameters": base_type(SchemaTypes.INTEGER)
            }
        }
    },
    "additionalProperties": False
}
