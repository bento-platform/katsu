# Individual schemas for validation of JSONField values

################################ Phenopackets based schemas ################################


ALLELE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:allele_schema",
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
    "$id": "chord_metadata_service:update_schema",
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
    "$id": "chord_metadata_service:ontology_class_schema",
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

ONTOLOGY_CLASS_LIST = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "ONTOLOGY_CLASS_LIST",
    "title": "Ontology class list",
    "description": "Ontology class list",
    "type": "array",
    "items": ONTOLOGY_CLASS,
}

EXTERNAL_REFERENCE = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:external_reference_schema",
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
    "$id": "chord_metadata_service:evidence_schema",
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


KEY_VALUE_OBJECT = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "KEY_VALUE_OBJECT",
    "title": "Key-value object",
    "description": "The schema represents a key-value object.",
    "type": "object",
    "patternProperties": {
        "^.*$": { "type": "string" }
    },
    "additionalProperties": False
}


AGE = {"type": "string", "description": "An ISO8601 string represent age."}

AGE_RANGE = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:age_range_schema",
    "title": "Age schema",
    "description": "An age range of a subject.",
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
    "$id": "chord_metadata_service:age_or_age_range_schema",
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
    "$id": "chord_metadata_service:disease_onset_schema",
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

### FHIR datatypes

# FHIR Quantity https://www.hl7.org/fhir/datatypes.html#Quantity
QUANTITY = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:quantity_schema",
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


# FHIR CodeableConcept https://www.hl7.org/fhir/datatypes.html#CodeableConcept
CODEABLE_CONCEPT = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:codeable_concept_schema",
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


# FHIR Period https://www.hl7.org/fhir/datatypes.html#Period
PERIOD = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:period_schema",
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


# FHIR Ratio https://www.hl7.org/fhir/datatypes.html#Ratio
RATIO = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:ratio",
    "title": "Ratio",
    "description": "Ratio schema.",
    "type": "object",
    "properties": {
        "numerator": QUANTITY,
        "denominator": QUANTITY
    },
    "additionalProperties": False
}


### FHIR based mCode elements

TIME_OR_PERIOD = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:time_or_period",
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


COMORBID_CONDITION = customize_schema(first_typeof=ONTOLOGY_CLASS, second_typeof=ONTOLOGY_CLASS,
                                     first_property="clinical_status", second_property="code",
                                     id="chord_metadata_service:comorbid_condition_schema",
                                     title="Comorbid Condition schema",
                                     description="Comorbid condition schema.")

#TODO this is definitely should be changed, fhir datatypes are too complex use Ontology_ class
COMPLEX_ONTOLOGY = customize_schema(first_typeof=ONTOLOGY_CLASS, second_typeof=ONTOLOGY_CLASS,
                                   first_property="data_value", second_property="staging_system",
                                   id="chord_metadata_service:complex_ontology_schema", title="Complex ontology",
                                   description="Complex object to combine data value and staging system.",
                                   required=["data_value"])

#TODO this is definitely should be changed, fhir datatypes are too complex use Ontology_ class
TUMOR_MARKER_TEST = customize_schema(first_typeof=ONTOLOGY_CLASS,
                                     second_typeof={
                                        "anyOf": [
                                            ONTOLOGY_CLASS,
                                            QUANTITY,
                                            RATIO
                                        ]
                                     },
                                     first_property="code", second_property="data_value",
                                     id="chord_metadata_service:tumor_marker_test",
                                     title="Tumor marker test",
                                     description="Tumor marker test schema.",
                                     required=["code"]
                                     )

