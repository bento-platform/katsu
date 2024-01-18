from pathlib import Path
from . import descriptions
from .description_utils import EXTRA_PROPERTIES, ONTOLOGY_CLASS as ONTOLOGY_CLASS_DESC
from .schema_utils import DATE_TIME, DRAFT_07, SCHEMA_TYPES, base_type, tag_ids_and_describe, \
    tag_schema_with_nested_ids, named_one_of, get_schema_app_id, sub_schema_uri

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
    "GESTATIONAL_AGE",
    "TIME_ELEMENT_SCHEMA"
]


# ======================== Phenopackets based schemas =========================

base_uri = get_schema_app_id(Path(__file__).parent.name)

ONTOLOGY_CLASS = tag_ids_and_describe({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "ontology_class"),
    "title": "Ontology class schema",
    "type": "object",
    "properties": {
        "id": base_type(SCHEMA_TYPES.STRING),
        "label": base_type(SCHEMA_TYPES.STRING)
    },
    "additionalProperties": False,
    "required": ["id", "label"]
}, ONTOLOGY_CLASS_DESC)

ONTOLOGY_CLASS_LIST = {
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "ontology_class_list"),
    "title": "Ontology class list",
    "description": "Ontology class list",
    "type": "array",
    "items": ONTOLOGY_CLASS,
}

CURIE_SCHEMA = {
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "curie"),
    "title": "Curie style string",
    "description": ("A [W3C Compact URI](https://www.w3.org/TR/curie/) formatted string. "
                    "A CURIE string has the structure ``prefix``:``reference``, as defined by the W3C syntax."),
    "type": "string",
    "pattern": "^\\w[^:]*:.+$",
    "additionalProperties": False,
}

KEY_VALUE_OBJECT = {
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "key_value_object"),
    "title": "Key-value object",
    "description": "The schema represents a key-value object.",
    "type": "object",
    "patternProperties": {
        "^.*$": {"type": "string"}
    },
    "additionalProperties": False
}

EXTRA_PROPERTIES_SCHEMA = tag_ids_and_describe({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "extra_properties"),
    "type": "object"
}, EXTRA_PROPERTIES)


AGE_STRING = tag_ids_and_describe({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "age_string"),
    "type": "string"
}, descriptions.AGE)

AGE = tag_ids_and_describe({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "age"),
    "title": "Age schema",
    "type": "object",
    "properties": {
        "iso8601duration": AGE_STRING
    },
    "additionalProperties": False,
    "required": ["iso8601duration"]
}, descriptions.AGE_NESTED)


AGE_RANGE = tag_ids_and_describe({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "age_range"),
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
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "age_or_age_range"),
    "title": "Age schema",
    "description": "An age object describing the age of the individual at the time of collection of biospecimens or "
                   "phenotypic observations.",
    "type": "object",
    "oneOf": [
        AGE,
        AGE_RANGE
    ]
}


TIME_INTERVAL = {
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "time_interval"),
    "title": "Age schema",
    "description": "An age object describing the age of the individual at the time of collection of biospecimens or "
                   "phenotypic observations.",
    "type": "object",
    "properties": {
        "start": DATE_TIME,
        "end": DATE_TIME
    },
    "additionalProperties": False,
    "required": ["start", "end"]
}


DISEASE_ONSET = {
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "disease_onset"),
    "title": "Onset age",
    "description": "Schema for the age of the onset of the disease.",
    "type": "object",
    "oneOf": [
        AGE,
        AGE_RANGE,
        ONTOLOGY_CLASS
    ]
}


GESTATIONAL_AGE = tag_ids_and_describe({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "gestational_age"),
    "title": "Gestational age schema",
    "type": "object",
    "properties": {
        "weeks": base_type(SCHEMA_TYPES.INTEGER),
        "days": base_type(SCHEMA_TYPES.INTEGER),
    },
    "required": ["weeks"]
}, descriptions.GESTATIONAL_AGE)


TIME_ELEMENT_SCHEMA = tag_ids_and_describe({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "time_element"),
    "title": "Time element schema",
    "type": "object",
    "oneOf": [
        named_one_of("gestational_age", GESTATIONAL_AGE),
        named_one_of("age", AGE),
        named_one_of("age_range", AGE_RANGE),
        named_one_of("ontology_class", ONTOLOGY_CLASS),
        named_one_of("timestamp", DATE_TIME),
        named_one_of("interval", TIME_INTERVAL)
    ]
}, descriptions.TIME_ELEMENT)


# ============================ FHIR INGEST SCHEMAS ============================
# The schema used to validate FHIR data for ingestion


FHIR_BUNDLE_SCHEMA = tag_schema_with_nested_ids({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "fhir_bundle"),
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
