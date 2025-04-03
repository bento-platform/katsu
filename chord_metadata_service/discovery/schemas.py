from django.conf import settings
from chord_metadata_service.restapi.schema_utils import (
    sub_schema_uri, array_of, base_type, SchemaTypes, enum_of
)

discovery_base_uri = sub_schema_uri(settings.SCHEMAS_BASE_URL, "discovery")

DISCOVERY_FIELD_SCHEMA = {
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
    "description": "Intermediate schema, enforces field schema with flexible names.",
    "type": "object",
    "patternProperties": {
        "^.*$": DISCOVERY_FIELD_SCHEMA
    },
    "additionalProperties": False
}

DISCOVERY_OVERVIEW_CHART_SCHEMA = {
    "description": "Associates a field name with a chart type for overview display",
    "type": "object",
    "properties": {
        "field": base_type(SchemaTypes.STRING),
        "chart_type": enum_of(["bar", "pie", "histogram"])
    },
    "additionalProperties": False
}

DISCOVERY_OVERVIEW_SCHEMA = {
    "description": "An overview section containing charts",
    "type": "object",
    "properties": {
        "section_title": base_type(SchemaTypes.STRING),
        "charts": array_of(DISCOVERY_OVERVIEW_CHART_SCHEMA)
    },
    "additionalProperties": False
}

DISCOVERY_SEARCH_SCHEMA = {
    "description": "Groups search fields by section.",
    "type": "object",
    "properties": {
        "section_title": base_type(SchemaTypes.STRING),
        "fields": array_of(base_type(SchemaTypes.STRING))
    },
    "additionalProperties": False
}

DISCOVERY_SCHEMA = {
    "$id": discovery_base_uri,
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
