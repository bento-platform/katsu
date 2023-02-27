from enum import Enum
from typing import List, Optional
from django.db import models

from .description_utils import describe_schema

__all__ = [
    "merge_schema_dictionaries",
    "search_optional_eq",
    "search_optional_str",
    "tag_schema_with_search_properties",
    "tag_schema_with_nested_ids",
    "tag_ids_and_describe",
    "customize_schema",
    "validation_schema_list",
    "array_of"
]

DRAFT_07 = "http://json-schema.org/draft-07/schema#"
CURIE_PATTERN = r"^[a-z0-9]+:[A-Za-z0-9.\-:]+$"

class SCHEMA_TYPES(Enum):
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    OBJECT = "object"
    NULL = "null"

class SCHEMA_STRING_FORMATS(Enum):
    """
    Json-schema supported string formats as enums
    See: https://json-schema.org/understanding-json-schema/reference/string.html#format
    """
    DATE_TIME = "date-time"
    TIME = "time"
    DATE = "date"
    DURATION = "duration"
    EMAIL = "email"
    IDN_EMAIL = "idn-email"
    HOSTNAME = "hostname"
    IDN_HOSTNAME = "idn-hostname"
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    UUID = "uuid"
    URI = "uri"
    URI_REFERENCE = "uri-reference"
    IRI = "iri"
    IRI_REFERENCE = "iri-reference"

def merge_schema_dictionaries(dict1: dict, dict2: dict):
    """
    Merges two dictionaries with the ~same structure (in this case, keys that
    are dictionaries in one should be dictionaries in the other.) Replaces any
    conflicts with the second dictionary's value.
    """
    res_dict = {**dict1}
    for k2, v2 in dict2.items():
        res_dict[k2] = merge_schema_dictionaries(dict1.get(k2, {}), v2) if isinstance(v2, dict) else v2
    return res_dict


def _searchable_field(operations: List[str], order: int, queryable: str = "all", multiple: bool = False):
    return {
        "operations": operations,
        "queryable": queryable,
        "canNegate": True,
        "required": False,
        "order": order,
        "type": "multiple" if multiple else "single"
    }


def search_optional_eq(order: int, queryable: str = "all"):
    return _searchable_field(["eq", "in"], order, queryable, multiple=False)


def search_optional_str(order: int, queryable: str = "all", multiple: bool = False):
    return _searchable_field(["eq", "ico", "in"], order, queryable, multiple)

def search_db_pk(model: models.Model):
    """
    Helper for search schema primary key definitions
    """
    return {
        "search": {
            **search_optional_eq(0),
            "database": {
                "field": model._meta.pk.column
            }
        }
    }

def search_db_fk(type: str, foreign_model: models.Model, field_name: str):
    return {
        "search": { "database": { "relationship": {
                    "type": type,
                    "foreign_key": foreign_model._meta.get_field(field_name).column
                }
            }
        }
    }

def search_table_ref(model: models.Model):
    return {
        "database": {
            "primary_key": model._meta.pk.column,
            "relation": model._meta.db_table
        }
    }

def tag_schema_with_search_properties(schema, search_descriptions: Optional[dict]):
    if not isinstance(schema, dict) or not search_descriptions:
        return schema

    if "type" not in schema:
        # TODO: handle oneOf, allOf, etc.
        return schema

    schema_with_search = {
        **schema,
        **({"search": search_descriptions["search"]} if "search" in search_descriptions else {}),
    }

    if schema["type"] == "object":
        return {
            **schema_with_search,
            **({
                "properties": {
                    p: tag_schema_with_search_properties(s, search_descriptions["properties"].get(p))
                    for p, s in schema["properties"].items()
                }
            } if "properties" in schema and "properties" in search_descriptions else {})
        }

    if schema["type"] == "array":
        return {
            **schema_with_search,
            **({"items": tag_schema_with_search_properties(schema["items"], search_descriptions["items"])}
               if "items" in schema and "items" in search_descriptions else {})
        }

    return schema_with_search


def tag_schema_with_nested_ids(schema: dict):
    if "$id" not in schema:
        raise ValueError("Schema to tag with nested IDs must have $id")

    schema_id = schema["$id"]
    schema_type = schema.get("type")

    if schema_type == "object":
        return {
            **schema,
            "properties": {
                k: tag_schema_with_nested_ids({**v, "$id": f"{schema_id}:{k}"} if "$id" not in v else v)
                for k, v in schema["properties"].items()
            },
        } if "properties" in schema else schema
    
    if schema_type == "array":
        return {
            **schema,
            "items": tag_schema_with_nested_ids({
                **schema["items"],
                "$id": f"{schema_id}:item",
            } if "$id" not in schema["items"] else schema["items"]),
        } if "items" in schema else schema

    # If nothing to tag, return itself (base case)
    return schema


def tag_ids_and_describe(schema: dict, descriptions: dict):
    return tag_schema_with_nested_ids(describe_schema(schema, descriptions))


class SchemaDefinitionsResolver:
    definitions = {}
    refs = {}
    schemas = None

    def __init__(self, definitions: dict, base_id="katsu:phenopackets", id_separator=":"):
        self.definitions = definitions
        self.base_id = base_id
        self.id_separator = id_separator
        self._merge_jsonschema_definitions()

    def resolve(self, schema_name: str):
        schema = self.schemas.get(schema_name)
        if "oneOf" in schema:
            one_ofs = [
                self.refs[one_of_item["$ref"]] if "$ref" in one_of_item else one_of_item
                for one_of_item in schema["oneOf"]
            ]
            schema = {**schema, "oneOf": one_ofs}
        if "properties" in schema:
            props = {
                prop_key: self.refs[prop_item["$ref"]] if "$ref" in prop_item else prop_item
                for prop_key, prop_item in schema["properties"].items()
            }
            schema = {**schema, "properties": props}
        return schema

    def _merge_jsonschema_definitions(self) -> dict:
        for (name, root_schema) in self.definitions["definitions"].items():
            ref_name = f"#/definitions/{name}"
            schema_id = self._make_id(name)
            self.refs[ref_name] = self._tag_jsonschema_with_nested_ids(schema=root_schema, schema_id=schema_id)
        self.schemas = {k.split("/")[-1].lower(): val for (k, val) in self.refs.items()}
        print("Json-schema definitions parsed.")

    def _tag_jsonschema_with_nested_ids(self, schema: dict, schema_id=None, discriminator=None):
        if schema_id:
            schema["$id"] = schema_id
        else:
            schema_id = schema.get("$id")

        if "$ref" in schema:
            return self._get_ref_or_def(schema.get("$ref"))

        schema_type = schema.get("type")
        discriminator = schema.get("discriminator", discriminator)

        if "oneOf" in schema:
            options = [
                self._tag_jsonschema_with_nested_ids(
                    schema=one_of_schema,
                    discriminator=discriminator)
                for one_of_schema in schema["oneOf"]
            ]
            schema = {
                **schema,
                "type": "object",
                "oneOf": options
            }

        # object, array, string
        if schema_type == "object" and "properties" in schema:
            return {
                **schema,
                "properties": {
                    k: self._tag_jsonschema_with_nested_ids(
                        schema=v,
                        schema_id=f"{schema_id}:{k}",
                        discriminator=discriminator
                    ) if "$id" not in v else v
                    for k, v in schema["properties"].items()
                }
            }

        if schema_type == "array" and "items" in schema:
            return {
                **schema,
                "items": self._tag_jsonschema_with_nested_ids(
                    schema={**schema["items"]} if "$id" not in schema["items"] else schema["items"],
                    discriminator=discriminator
                )
            }

        return schema

    def _get_ref_or_def(self, ref_name: str):
        if ref_name in self.refs:
            return self.refs[ref_name]
        else:
            def_name = ref_name.split("/")[-1]
            schema_def = self.definitions["definitions"][def_name]
            schema = self._tag_jsonschema_with_nested_ids(schema=schema_def, schema_id=self._make_id(def_name))
            self.refs[ref_name] = schema
            return schema

    def _make_id(self, name: str):
        return f"{self.base_id}{self.id_separator}{name}"


def customize_schema(first_typeof: dict, second_typeof: dict, first_property: str, second_property: str,
                     schema_id: str = None, title: str = None, description: str = None,
                     additional_properties: bool = False, required:List[str]=None) -> dict:
    return {
        "$schema": DRAFT_07,
        "$id": schema_id,
        "title": title,
        "description": description,
        "type": "object",
        "properties": {
            first_property: first_typeof,
            second_property: second_typeof
        },
        "required": required or [],
        "additionalProperties": additional_properties
    }


def make_object_schema(properties: dict, schema_id: str = None, title: str = None, description:str = None,
                        additional_properties: bool = False, required:List[str] = None) -> dict:
    return {
        "$schema": DRAFT_07,
        "$id": schema_id,
        "title": title,
        "description": description,
        "type": "object",
        "properties": properties,
        "required": required or [],
        "additionalProperties": additional_properties
    }


def describe_schema_opt(schema: dict, description: str):
    """ Optionally adds a description entry to a schema dict """
    if description:
        return {
            **schema,
            "description": description
        }
    else:
        return schema


def validation_schema_list(schema):
    """ Schema to validate JSON array values. """

    return {
        "$schema": DRAFT_07,
        "$id": "chord_metadata_service:schema_list",
        "title": "Schema list",
        "type": "array",
        "items": schema
    }


def array_of(item, description=""):
    """
    Simple array schema with items schema specified by argument.
    Use to simplify/shorthen json-schema writing.
    """
    schema = {
        "type": "array",
        "items": item
    }
    return describe_schema_opt(schema, description)


def enum_of(values: List[str], description=""):
    schema = {
        "type": "string",
        "enum": values
    }
    return describe_schema_opt(schema, description)


def base_type(type: SCHEMA_TYPES, description=""):
    """
    Creates a basic type schema
    """
    return describe_schema_opt({"type": type.value}, description)


def string_with_pattern(pattern: str, description=""):
    """
    Creates a regex formated string schema
    """
    schema = {
        "type": "string",
        "pattern": pattern
    }
    return describe_schema_opt(schema, description)


def string_with_format(format: SCHEMA_STRING_FORMATS, description=""):
    schema = {
        "type": "string",
        "format": format.value
    }
    return describe_schema_opt(schema, description)


def named_one_of(prop_name: str, prop_schema: dict):
    """
    Returns a schema valid as a oneOf object item for a specific property name
    """
    return {
        "type": "object",
        "properties": {
            prop_name: prop_schema
        },
        "required": [prop_name]
    }


DATE_TIME = string_with_format(SCHEMA_STRING_FORMATS.DATE_TIME)
CURIE_SCHEMA = string_with_pattern(CURIE_PATTERN)
