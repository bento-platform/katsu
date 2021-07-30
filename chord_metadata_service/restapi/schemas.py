from . import descriptions
from .description_utils import EXTRA_PROPERTIES, ONTOLOGY_CLASS as ONTOLOGY_CLASS_DESC
from .schema_utils import tag_ids_and_describe, tag_schema_with_nested_ids

# Individual schemas for validation of JSONField values


__all__ = [
    "ONTOLOGY_CLASS",
    "ONTOLOGY_CLASS_LIST",
    "KEY_VALUE_OBJECT",
    "AGE_STRING",
    "AGE",
    "AGE_RANGE",
    "AGE_OR_AGE_RANGE",
    "EXTRA_PROPERTIES_SCHEMA",
    "FHIR_BUNDLE_SCHEMA",
]


# ======================== Phenopackets based schemas =========================


ONTOLOGY_CLASS = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:common:ontology_class",
    "title": "Ontology class schema",
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "label": {"type": "string"}
    },
    "additionalProperties": False,
    "required": ["id", "label"]
}, ONTOLOGY_CLASS_DESC)

ONTOLOGY_CLASS_LIST = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:common:ontology_class_list",
    "title": "Ontology class list",
    "description": "Ontology class list",
    "type": "array",
    "items": ONTOLOGY_CLASS,
}


KEY_VALUE_OBJECT = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:common:key_value_object",
    "title": "Key-value object",
    "description": "The schema represents a key-value object.",
    "type": "object",
    "patternProperties": {
        "^.*$": {"type": "string"}
    },
    "additionalProperties": False
}

EXTRA_PROPERTIES_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:common:extra_properties",
    "type": "object"
}, EXTRA_PROPERTIES)


AGE_STRING = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:common:age_string",
    "type": "string"
}, descriptions.AGE)

AGE = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:common:age",
    "title": "Age schema",
    "type": "object",
    "properties": {
        "age": AGE_STRING
    },
    "additionalProperties": False,
    "required": ["age"]
}, descriptions.AGE_NESTED)


AGE_RANGE = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:common:age_range",
    "title": "Age range schema",
    "type": "object",
    "properties": {
        "start": AGE,
        "end": AGE,
    },
    "additionalProperties": False,
    "required": ["start", "end"]
}, descriptions.AGE_RANGE)


AGE_OR_AGE_RANGE = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:common:age_or_age_range",
    "title": "Age schema",
    "description": "An age object describing the age of the individual at the time of collection of biospecimens or "
                   "phenotypic observations.",
    "type": "object",
    "oneOf": [
        AGE,
        AGE_RANGE
    ]
}

DISEASE_ONSET = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:common:disease_onset",
    "title": "Onset age",
    "description": "Schema for the age of the onset of the disease.",
    "type": "object",
    "oneOf": [
        AGE,
        AGE_RANGE,
        ONTOLOGY_CLASS
    ]
}


# ============================ FHIR INGEST SCHEMAS ============================
# The schema used to validate FHIR data for ingestion


FHIR_BUNDLE_SCHEMA = tag_schema_with_nested_ids({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:common:fhir_bundle",
    "description": "FHIR Bundle schema",
    "type": "object",
    "properties": {
        "resourceType": {
            "type": "string",
            "const": "Bundle",
            "description": "Collection of resources."
        },
        "entry": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "resource": {"type": "object"}
                },
                "additionalProperties": True,
                "required": ["resource"]
            }
        }
    },
    "additionalProperties": True,
    "required": ["resourceType", "entry"]
})
