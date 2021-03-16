from .descriptions import EXPERIMENT
from chord_metadata_service.restapi.description_utils import describe_schema
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS_LIST, KEY_VALUE_OBJECT


__all__ = ["EXPERIMENT_SCHEMA"]


EXPERIMENT_SCHEMA = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:experiment_schema",
    "title": "Experiment schema",
    "description": "Schema for describing an experiment.",
    "type": "object",
    "properties": {
        "id": {
            "type": "string"
        },
        "reference_registry_id": {
            "type": "string"
        },
        "qc_flags": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "experiment_type": {
            "type": "string"
        },
        "experiment_ontology": ONTOLOGY_CLASS_LIST,
        "molecule": {
            "type": "string"
        },
        "molecule_ontology": ONTOLOGY_CLASS_LIST,
        "library_strategy": {
            "type": "string"
        },
        "extraction_protocol": {
            "type": "string"
        },
        "file_location": {
            "type": "string"
        },
        "extra_properties": KEY_VALUE_OBJECT,
        "biosample": {
            "type": "string"
        },
    },
    "required": ["id", "experiment_type", "library_strategy"]
}, EXPERIMENT)
