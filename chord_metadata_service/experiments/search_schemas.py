from . import models, schemas
from chord_metadata_service.restapi.schema_utils import (
    search_optional_eq,
    search_optional_str,
    tag_schema_with_search_properties,
)
from chord_metadata_service.restapi.search_schemas import ONTOLOGY_SEARCH_SCHEMA


__all__ = ["EXPERIMENT_SEARCH_SCHEMA"]


EXPERIMENT_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.EXPERIMENT_SCHEMA, {
    "properties": {
        "id": {
            "search": {"database": {"field": models.Experiment._meta.pk.column}}
        },
        "reference_registry_id": {
            "search": search_optional_str(0, queryable="internal"),
        },
        "qc_flags": {
            "items": {
                "search": search_optional_str(0),
            },
            "search": {"database": {"type": "array"}}
        },
        "experiment_type": {
            "search": search_optional_str(1, queryable="internal"),
        },
        "experiment_ontology": {
            "items": ONTOLOGY_SEARCH_SCHEMA,  # TODO: Specific ontology?
            "search": {"database": {"type": "jsonb"}}
        },
        "molecule": {
            "search": search_optional_eq(2),
        },
        "molecule_ontology": {
            "items": ONTOLOGY_SEARCH_SCHEMA,  # TODO: Specific ontology?
            "search": {"database": {"type": "jsonb"}}
        },
        "library_strategy": {
            "search": search_optional_eq(3),
        },
        # TODO: other_fields: ?
        "biosample": {
            "search": search_optional_eq(4, queryable="internal"),
        },
    },
    "search": {
        "database": {
            "relation": models.Experiment._meta.db_table,
            "primary_key": models.Experiment._meta.pk.column,
        }
    }
})
