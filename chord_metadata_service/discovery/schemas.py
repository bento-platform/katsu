from pathlib import Path
from chord_metadata_service.restapi.schema_utils import (
    get_schema_app_id, sub_schema_uri, array_of, base_type, SchemaTypes, enum_of
)

base_uri = get_schema_app_id(Path(__file__).parent.name)

DISCOVERY_FIELD_SCHEMA = {
    "$id": sub_schema_uri(base_uri, "discovery_field"),
    "description": "Field configuration",
    "type": "object",
    "properties": {
        "mapping": base_type(SchemaTypes.STRING),
        "mapping_for_search_filter": base_type(SchemaTypes.STRING),
        "group_by": base_type(SchemaTypes.STRING),
        "group_by_value": base_type(SchemaTypes.STRING),
        "value_mapping": base_type(SchemaTypes.STRING),
        "title": base_type(SchemaTypes.STRING),
        "description": base_type(SchemaTypes.STRING),
        "datatype": enum_of(["number", "string", "date"]),
        "config": {
            "type": "object",
            "properties": {
                # datatype == string
                "enum": {
                    "oneOf": [
                        # either an array of strings, or null
                        array_of(base_type(SchemaTypes.STRING)),
                        base_type(SchemaTypes.NULL)
                    ]
                },
                # datatype == number
                "bins": array_of(base_type(SchemaTypes.NUMBER)),
                "bin_size": base_type(SchemaTypes.NUMBER),
                "taper_left": base_type(SchemaTypes.NUMBER),
                "taper_right": base_type(SchemaTypes.NUMBER),
                "units": base_type(SchemaTypes.STRING),
                "minimum": base_type(SchemaTypes.NUMBER),
                "maximum": base_type(SchemaTypes.NUMBER),
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
        "^.*$": DISCOVERY_FIELD_SCHEMA
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

DISCOVERY_SEARCH_SCHEMA = {
    "$id": sub_schema_uri(base_uri, "discovery_search"),
    "description": "Groups search fields by section.",
    "type": "object",
    "properties": {
        "section_title": base_type(SchemaTypes.STRING),
        "fields": array_of(base_type(SchemaTypes.STRING))
    },
    "additionalProperties": False
}

DISCOVERY_SCHEMA = {
    "$id": sub_schema_uri(base_uri, "discovery"),
    "description": "Discovery configuration for public fields/search",
    "type": "object",
    "properties": {
        "overview": array_of(DISCOVERY_OVERVIEW_SCHEMA, "List of overview sections"),
        "search": array_of(DISCOVERY_SEARCH_SCHEMA),
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

# import json
# with open("discovery.json", "w") as schema_file:
#     json.dump(DISCOVERY_SCHEMA, schema_file)
