from typing import TypedDict

__all__ = [
    "ExtensionSchemaDict",
]


class ExtensionSchemaDict(TypedDict):
    json_schema: dict
    required: bool
    schema_type: str
