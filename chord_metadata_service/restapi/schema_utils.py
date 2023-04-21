from bento_lib.search import queries as q
from .description_utils import describe_schema
from typing import List, Optional

__all__ = [
    "merge_schema_dictionaries",
    "search_optional_eq",
    "search_optional_str",
    "tag_schema_with_search_properties",
    "tag_schema_with_nested_ids",
    "tag_ids_and_describe",
    "customize_schema",
    "schema_list",
]


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
    return _searchable_field([q.SEARCH_OP_EQ, q.SEARCH_OP_IN], order, queryable, multiple=False)


def search_optional_str(order: int, queryable: str = "all", multiple: bool = False):
    return _searchable_field([
        q.SEARCH_OP_EQ,
        q.SEARCH_OP_ICO,
        q.SEARCH_OP_IN,
        q.SEARCH_OP_ISW,
        q.SEARCH_OP_IEW,
        q.SEARCH_OP_ILIKE,
    ], order, queryable, multiple)


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


def customize_schema(first_typeof: dict, second_typeof: dict, first_property: str, second_property: str,
                     schema_id: str = None, title: str = None, description: str = None,
                     additional_properties: bool = False, required=None) -> dict:
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
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


def schema_list(schema):
    """ Schema to validate JSON array values. """

    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "chord_metadata_service:schema_list",
        "title": "Schema list",
        "type": "array",
        "items": schema
    }


def patch_project_schemas(base_schema: dict, extension_schemas: dict[str, object]) -> dict:
    if "$id" not in base_schema:
        raise ValueError("Schema to patch with extra_properties schemas must have valid $id")

    if not isinstance(base_schema, dict) or "type" not in base_schema:
        return base_schema

    # Get the last term of the schema $id to match with SchemaType
    # e.g. 'katsu:phenopackets:phenopacket' -> 'phenopacket'
    schema_id = base_schema["$id"].split(":")[-1]
    
    patched_schema = {**base_schema}
    if patched_schema["type"] == "object":
        # TODO: recursively patch schema if applicablex
        if schema_id in extension_schemas:
            ext_schema = extension_schemas[schema_id]
            patched_schema = {
                **patched_schema,
                "extra_properties": ext_schema.json_schema,
            }

            if ext_schema.required:
                default_required = patched_schema.get("required", [])
                default_required.append("extra_properties")
                patched_schema["required"] = default_required

    if patched_schema["type"] == "array":
        # TODO: recursively patch schema if applicable
        pass
    
    return patched_schema
