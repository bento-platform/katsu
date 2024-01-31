from .schemas import ONTOLOGY_CLASS, TIME_ELEMENT_SCHEMA
from .schema_utils import SEARCH_DATABASE_JSONB, search_optional_str, tag_schema_with_search_properties

__all__ = [
    "ONTOLOGY_SEARCH_SCHEMA",
    "TIME_ELEMENT_SEARCH_SCHEMA",
]

ONTOLOGY_SEARCH_SCHEMA = tag_schema_with_search_properties(ONTOLOGY_CLASS, {
    "properties": {
        "id": {
            "search": search_optional_str(0, multiple=True)
        },
        "label": {
            "search": search_optional_str(1, multiple=True)
        }
    },
    "search": SEARCH_DATABASE_JSONB
})

TIME_ELEMENT_SEARCH_SCHEMA = tag_schema_with_search_properties(TIME_ELEMENT_SCHEMA, {
    "oneOf": [],
    "search": SEARCH_DATABASE_JSONB
})
