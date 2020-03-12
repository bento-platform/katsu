from typing import List


# Individual schemas for validation of JSONField values

################################ Phenopackets based schemas ################################


ALLELE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "todo",
    "title": "Allele schema",
    "description": "Variant allele types",
    "type": "object",
    "properties": {
        "id": {"type": "string"},

        "hgvs": {"type": "string"},

        "genome_assembly": {"type": "string"},
        "chr": {"type": "string"},
        "pos": {"type": "integer"},
        "re": {"type": "string"},
        "alt": {"type": "string"},
        "info": {"type": "string"},

        "seq_id": {"type": "string"},
        "position": {"type": "integer"},
        "deleted_sequence": {"type": "string"},
        "inserted_sequence": {"type": "string"},

        "iscn": {"type": "string"}
    },
    "additionalProperties": False,
    "oneOf": [
        {
            "required": ["hgvs"]
        },
        {
            "required": ["genome_assembly"]
        },
        {
            "required": ["seq_id"]
        },
        {
            "required": ["iscn"]
        }

    ],
    "dependencies": {
        "genome_assembly": ["chr", "pos", "re", "alt", "info"],
        "seq_id": ["position", "deleted_sequence", "inserted_sequence"]
    }
}

UPDATE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "todo",
    "title": "Updates schema",
    "description": "Schema to check incoming updates format",
    "type": "object",
    "properties": {
        "timestamp": {"type": "string", "format": "date-time",
                      "description": "ISO8601 UTC timestamp at which this record was updated."},
        "updated_by": {"type": "string", "description": "Who updated the phenopacket"},
        "comment": {"type": "string", "description": "Comment about updates or reasons for an update."}
    },
    "additionalProperties": False,
    "required": ["timestamp", "comment"]
}

ONTOLOGY_CLASS = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "todo",
    "title": "Ontology class schema",
    "description": "todo",
    "type": "object",
    "properties": {
        "id": {"type": "string", "description": "CURIE style identifier."},
        "label": {"type": "string", "description": "Human-readable class name."}
    },
    "additionalProperties": False,
    "required": ["id", "label"]
}

EXTERNAL_REFERENCE = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "todo",
    "title": "External reference schema",
    "description": "The schema encodes information about an external reference.",
    "type": "object",
    "properties": {
        "id": {"type": "string", "description": "An application specific identifier."},
        "description": {"type": "string", "description": "An application specific description."}
    },
    "additionalProperties": False,
    "required": ["id"]
}

EVIDENCE = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "todo",
    "title": "Evidence schema",
    "description": "The schema represents the evidence for an assertion such as an observation of a PhenotypicFeature.",
    "type": "object",
    "properties": {
        "evidence_code": {
            "type": "object",
            "description": "An ontology class that represents the evidence type.",
            "properties": {
                "id": {"type": "string", "description": "CURIE style identifier."},
                "label": {"type": "string", "description": "Human-readable class name."}
            },
            "additionalProperties": False,
            "required": ["id", "label"]
        },
        "reference": {
            "type": "object",
            "description": "Representation of the source of the evidence.",
            "properties": {
                "id": {"type": "string", "description": "An application specific identifier."},
                "description": {"type": "string", "description": "An application specific description."}
            },
            "additionalProperties": False,
            "required": ["id"]
        }
    },
    "additionalProperties": False,
    "required": ["evidence_code"]
}

AGE = {"type": "string", "description": "An ISO8601 string represent age."}

AGE_RANGE = {
    "type": "object",
    "properties": {
        "start": {
            "type": "object",
            "properties": {
                "age": AGE
            }
        },
        "end": {
            "type": "object",
            "properties": {
                "age": AGE
            }
        }
    },
    "additionalProperties": False,
    "required": ["start", "end"]
}

AGE_OR_AGE_RANGE = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "todo",
    "title": "Age schema",
    "description": "An age object describing the age of the individual at the time of collection of biospecimens or "
                   "phenotypic observations.",
    "type": "object",
    "properties": {
        "age": {
            "anyOf": [
                AGE,
                AGE_RANGE
            ]
        }
    },
    "additionalProperties": False
}

DISEASE_ONSET = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "todo",
    "title": "Onset age",
    "description": "Schema for the age of the onset of the disease.",
    "type": "object",
    "properties": {
        "age": {
            "anyOf": [
                AGE,
                AGE_RANGE,
                ONTOLOGY_CLASS
            ]
        }
    },
    "additionalProperties": False
}

################################## mCode/FHIR based schemas ##################################


# mCode/FHIR Quantity

QUANTITY = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "todo",
    "title": "Quantity schema",
    "description": "Schema for the datatype Quantity.",
    "type": "object",
    "properties": {
        "value": {
            "type": "number"
        },
        "comparator": {
            "enum": ["<", ">", "<=", ">=", "="]
        },
        "unit": {
            "type": "string"
        },
        "system": {
            "type": "string",
            "format": "uri"
        },
        "code": {
            "type": "string"
        }
    },
    "additionalProperties": False
}

# mCode/FHIR CodeableConcept

CODEABLE_CONCEPT = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "todo",
    "title": "Codeable Concept schema",
    "description": "Schema for the datatype Concept.",
    "type": "object",
    "properties": {
        "coding": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "system": {"type": "string", "format": "uri"},
                    "version": {"type": "string"},
                    "code": {"type": "string"},
                    "display": {"type": "string"},
                    "user_selected": {"type": "boolean"}
                }
            }
        },
        "text": {
            "type": "string"
        }
    },
    "additionalProperties": False
}


PERIOD = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "todo",
    "title": "Period",
    "description": "Period schema.",
    "type": "object",
    "properties": {
        "start": {
            "type": "string",
            "format": "date-time"
        },
        "end": {
            "type": "string",
            "format": "date-time"
        }
    },
    "additionalProperties": False
}


TIME_OR_PERIOD = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "todo",
    "title": "Time of Period",
    "description": "Time of Period schema.",
    "type": "object",
    "properties": {
        "value": {
            "anyOf": [
                {"type": "string", "format": "date-time"},
                PERIOD
            ]
        }
    },
    "additionalProperties": False
}


def customize_schema(first_typeof: dict, second_typeof: dict, first_property: str, second_property: str,
                    id: str=None, title: str=None, description: str=None, additionalProperties=False,
                    required=None) -> dict:
    if required is None:
        required = []
    return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": id,
            "title": title,
            "description": description,
            "type": "object",
            "properties": {
                first_property: first_typeof,
                second_property: second_typeof
            },
            "required": required,
            "additionalProperties": additionalProperties
            }


COMORBID_CONDITION = customize_schema(first_typeof=CODEABLE_CONCEPT, second_typeof=CODEABLE_CONCEPT,
                                     first_property="clinical_status", second_property="code",
                                     id="chord_metadata_service:comorbid_condition_schema",
                                     title="Comorbid Condition schema",
                                     description="Comorbid condition schema.")


COMPLEX_ONTOLOGY = customize_schema(first_typeof=CODEABLE_CONCEPT, second_typeof=CODEABLE_CONCEPT,
                                   first_property="data_value", second_property="staging_system",
                                   id="chord_metadata_service:complex_ontology_schema", title="Complex ontology",
                                   description="Complex object to combine data value and staging system.",
                                   required=["data_value"])
