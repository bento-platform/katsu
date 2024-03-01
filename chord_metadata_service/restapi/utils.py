from __future__ import annotations
from typing import Any, TypedDict

LENGTH_Y_M = 4 + 1 + 2  # dates stored as yyyy-mm-dd

COMPUTED_PROPERTY_PREFIX = "__"


class BinWithValue(TypedDict):
    label: str
    value: int


def camel_case_field_names(string) -> str:
    """ Function to convert snake_case field names to camelCase """
    # Capitalize every part except the first
    return "".join(
        part.title() if i > 0 else part
        for i, part in enumerate(string.split("_"))
    )


# TODO: Typing: generics
def transform_keys(obj: Any) -> Any:
    """
    The function validates against DATS schemas that use camelCase.
    It iterates over a dict and changes all keys in nested objects to camelCase.
    """

    if isinstance(obj, list):
        return [transform_keys(i) for i in obj]

    if isinstance(obj, dict):
        return {
            camel_case_field_names(key): transform_keys(value)
            for key, value in obj.items()
        }

    return obj


def computed_property(name: str):
    """
    Takes a name and returns it prefixed with "__"
    """
    return COMPUTED_PROPERTY_PREFIX + name
