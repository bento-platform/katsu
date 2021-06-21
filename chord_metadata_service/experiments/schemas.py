from .descriptions import EXPERIMENT, EXPERIMENT_RESULT
from chord_metadata_service.restapi.description_utils import describe_schema
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS_LIST, KEY_VALUE_OBJECT


__all__ = ["EXPERIMENT_SCHEMA"]


EXPERIMENT_RESULT_SCHEMA = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:experiment_result_schema",
    "title": "Experiment result schema",
    "description": "Schema for describing information about analysis of sequencing data in a file format.",
    "type": "object",
    "properties": {
        "identifier": {
            "type": "string"
        },
        "description": {
            "type": "string"
        },
        "filename": {
            "type": "string"
        },
        "file_format": {
            "type": "string",
            "enum": []
        },
        "data_output_type": {
            "type": "string",
            "enum": []
        },
        "creation_date": {
            "type": "string"
        },
        "created_by": {
            "type": "string"
        },
        "extra_properties": KEY_VALUE_OBJECT,
    }
}, EXPERIMENT_RESULT)


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
        "study_type": {
            "type": "string"
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
        "library_source": {
            "type": "string"
        },
        "library_selection": {
            "type": "string"
        },
        "library_layout": {
            "type": "string"
        },
        "extraction_protocol": {
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
        "extra_properties": KEY_VALUE_OBJECT,
        "biosample": {
            "type": "string"
        },
        "experiment_results":{
            "type": "array",
            "items": EXPERIMENT_RESULT_SCHEMA
        },
    },
    "required": ["id", "experiment_type", "library_strategy"]
}, EXPERIMENT)
