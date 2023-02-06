# Individual schemas for validation of JSONField values

from chord_metadata_service.patients.schemas import INDIVIDUAL_SCHEMA
from chord_metadata_service.resources.schemas import RESOURCE_SCHEMA
from chord_metadata_service.restapi.schemas import (
    AGE,
    AGE_RANGE,
    AGE_OR_AGE_RANGE,
    EXTRA_PROPERTIES_SCHEMA,
    ONTOLOGY_CLASS,
    TIME_INTERVAL,
)
from chord_metadata_service.restapi.schema_utils import tag_ids_and_describe

from . import descriptions


__all__ = [
    "ALLELE_SCHEMA",
    "PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA",
    "PHENOPACKET_UPDATE_SCHEMA",
    "PHENOPACKET_META_DATA_SCHEMA",
    "PHENOPACKET_EVIDENCE_SCHEMA",
    "PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA",
    "PHENOPACKET_GENE_SCHEMA",
    "PHENOPACKET_HTS_FILE_SCHEMA",
    "PHENOPACKET_VARIANT_SCHEMA",
    "PHENOPACKET_BIOSAMPLE_SCHEMA",
    "PHENOPACKET_DISEASE_ONSET_SCHEMA",
    "PHENOPACKET_DISEASE_SCHEMA",
    "PHENOPACKET_SCHEMA",
    "PHENOPACKET_GESTATIONAL_AGE",
    "PHENOPACKET_TIME_ELEMENT_SCHEMA",
    "PHENOPACKET_PROCEDURE_SCHEMA",
    "PHENOPACKET_QUANTITY_SCHEMA",
    "PHENOPACKET_TYPED_QUANTITY_SCHEMA",
    "PHENOPACKET_VALUE_SCHEMA",
    "PHENOPACKET_COMPLEX_VALUE_SCHEMA",
    "PHENOPACKET_MEASUREMENT_VALUE_SCHEMA",
    "PHENOPACKET_MEASUREMENT_SCHEMA",
    "PHENOPACKET_TREATMENT",
    "PHENOPACKET_RADIATION_THERAPY",
    "PHENOPACKET_THERAPEUTIC_REGIMEN",
    "PHENOPACKET_MEDICAL_ACTION_SCHEMA"
]


ALLELE_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:allele",
    "title": "Allele schema",
    "description": "Variant allele types",
    "type": "object",
    "properties": {
        "id": {"type": "string"},

        "hgvs": {"type": "string"},

        "genome_assembly": {"type": "string"},
        "chr": {"type": "string"},
        "pos": {"type": "integer"},
        "ref": {"type": "string"},
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
        {"required": ["hgvs"]},
        {"required": ["genome_assembly"]},
        {"required": ["seq_id"]},
        {"required": ["iscn"]}
    ],
    "dependencies": {
        "genome_assembly": ["chr", "pos", "ref", "alt", "info"],
        "seq_id": ["position", "deleted_sequence", "inserted_sequence"]
    }
}, descriptions.ALLELE)


PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:external_reference",
    "title": "External reference schema",
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
        },
        "description": {
            "type": "string",
        }
    },
    "required": ["id"]
}, descriptions.EXTERNAL_REFERENCE)


PHENOPACKET_UPDATE_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:update",
    "title": "Updates schema",
    "type": "object",
    "properties": {
        "timestamp": {
            "type": "string",
            "format": "date-time"
        },
        "updated_by": {
            "type": "string",
        },
        "comment": {
            "type": "string",
        }
    },
    "additionalProperties": False,
    "required": ["timestamp", "comment"],
}, descriptions.UPDATE)


# noinspection PyProtectedMember
PHENOPACKET_META_DATA_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:meta_data",
    "type": "object",
    "properties": {
        "created": {
            "type": "string",
            "format": "date-time"
        },
        "created_by": {
            "type": "string",
        },
        "submitted_by": {
            "type": "string",
        },
        "resources": {
            "type": "array",
            "items": RESOURCE_SCHEMA,
        },
        "updates": {
            "type": "array",
            "items": PHENOPACKET_UPDATE_SCHEMA,
        },
        "phenopacket_schema_version": {
            "type": "string",
        },
        "external_references": {
            "type": "array",
            "items": PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA
        },
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
}, descriptions.META_DATA)

PHENOPACKET_EVIDENCE_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:evidence",
    "title": "Evidence schema",
    "type": "object",
    "properties": {
        "evidence_code": ONTOLOGY_CLASS,
        "reference": PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA
    },
    "additionalProperties": False,
    "required": ["evidence_code"],
}, descriptions.EVIDENCE)

PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:phenotypic_feature",
    "type": "object",
    "properties": {
        "description": {
            "type": "string",
        },
        "type": ONTOLOGY_CLASS,
        "negated": {
            "type": "boolean",
        },
        "severity": ONTOLOGY_CLASS,
        "modifier": {  # TODO: Plural?
            "type": "array",
            "items": ONTOLOGY_CLASS
        },
        "onset": ONTOLOGY_CLASS,
        "evidence": PHENOPACKET_EVIDENCE_SCHEMA,
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
}, descriptions.PHENOTYPIC_FEATURE)

# TODO: search
PHENOPACKET_GENE_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:gene",
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
        },
        "alternate_ids": {
            "type": "array",
            "items": {
                "type": "string",
            }
        },
        "symbol": {
            "type": "string",
        },
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["id", "symbol"]
}, descriptions.GENE)

PHENOPACKET_HTS_FILE_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:hts_file",
    "type": "object",
    "properties": {
        "uri": {
            "type": "string"  # TODO: URI pattern
        },
        "description": {
            "type": "string"
        },
        "hts_format": {
            "type": "string",
            "enum": ["SAM", "BAM", "CRAM", "VCF", "BCF", "GVCF", "FASTQ", "UNKNOWN"]
        },
        "genome_assembly": {
            "type": "string"
        },
        "individual_to_sample_identifiers": {
            "type": "object"  # TODO
        },
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    }
}, descriptions.HTS_FILE)

# TODO: search??
PHENOPACKET_VARIANT_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:variant",
    "type": "object",  # TODO
    "properties": {
        "allele": ALLELE_SCHEMA,  # TODO
        "zygosity": ONTOLOGY_CLASS,
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    }
}, descriptions.VARIANT)

PHENOPACKET_GESTATIONAL_AGE = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:gestational_age",
    "title": "Gestational age schema",
    "type": "object",
    "properties": {
        "weeks": {
            "type": "integer"
        },
        "days": {
            "type": "integer"
        }
    },
    "required": ["weeks"]
}, {}) #TODO: description

PHENOPACKET_TIME_ELEMENT_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:time_element",
    "title": "Time element schema",
    "type": "object",
    "oneOf": [
        PHENOPACKET_GESTATIONAL_AGE,
        AGE,
        AGE_RANGE,
        ONTOLOGY_CLASS,
        {
            "type": "string",
            "format": "date-tm"
        },
        TIME_INTERVAL
    ],
    "required": ["oneOf"]
}, {}) #TODO: description

PHENOPACKET_PROCEDURE_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:procedure",
    "title": "Procedure schema",
    "type": "object",
    "properties": {
        "code": ONTOLOGY_CLASS,
        "body_site": ONTOLOGY_CLASS,
        "performed": PHENOPACKET_TIME_ELEMENT_SCHEMA
    },
    "required": ["code"],
}, descriptions=descriptions.PROCEDURE)

PHENOPACKET_QUANTITY_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:quantity",
    "title": "Quantity schema",
    "type": "object",
    "properties": {
        "unit": ONTOLOGY_CLASS,
        "value": {
            "type": "number"
        },
        "reference_range": {
            "unit": ONTOLOGY_CLASS,
            "low": {
                "type": "number"
            },
            "high": {
                "type": "number"
            }
        }
    },
    "required": ["unit", "value"]
}

PHENOPACKET_TYPED_QUANTITY_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:typed-quantity",
    "title": "Quantity schema",
    "type": "object",
    "properties": {
        "type": ONTOLOGY_CLASS,
        "quantity": PHENOPACKET_QUANTITY_SCHEMA
    },
    "required": ["type", "quantity"]
}

PHENOPACKET_VALUE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:value",
    "title": "Value schema",
    "type": "object",
    "oneOf": [
        PHENOPACKET_QUANTITY_SCHEMA,
        ONTOLOGY_CLASS
    ],
    "required": ["oneOf"]
}

PHENOPACKET_COMPLEX_VALUE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:complex_value",
    "title": "Complex value schema",
    "type": "object",
    "properties": {
        "typed_quantities": {
            "type": "array",
            "items": PHENOPACKET_TYPED_QUANTITY_SCHEMA
        }
    },
    "required": ["typed_quantities"]
}

PHENOPACKET_MEASUREMENT_VALUE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:measurement:measurement_value",
    "title": "Measurement value schema",
    "type": "object",
    "oneOf": [
        PHENOPACKET_VALUE_SCHEMA,
        PHENOPACKET_COMPLEX_VALUE_SCHEMA
    ],
    "required": ["oneOf"]
}

PHENOPACKET_MEASUREMENT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:measurement",
    "title": "Measurement schema",
    "type": "object",
    "properties": {
        "description": {"type": "string"},
        "assay": ONTOLOGY_CLASS,
        "measurement_value": PHENOPACKET_MEASUREMENT_VALUE_SCHEMA,
        "time_observed": PHENOPACKET_TIME_ELEMENT_SCHEMA,
        "procedure": PHENOPACKET_PROCEDURE_SCHEMA
    },
    "required": ["assay", "measurement_value"]
}

# noinspection PyProtectedMember
PHENOPACKET_BIOSAMPLE_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:biosample",
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
        },
        "individual_id": {
            "type": "string",
        },
        "description": {
            "type": "string",
        },
        "sampled_tissue": ONTOLOGY_CLASS,
        "phenotypic_features": {
            "type": "array",
            "items": PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA,
        },
        "taxonomy": ONTOLOGY_CLASS,
        "individual_age_at_collection": AGE_OR_AGE_RANGE,
        "histological_diagnosis": ONTOLOGY_CLASS,
        "tumor_progression": ONTOLOGY_CLASS,
        "tumor_grade": ONTOLOGY_CLASS,  # TODO: Is this a list?
        "diagnostic_markers": {
            "type": "array",
            "items": ONTOLOGY_CLASS,
        },
        "procedure": {
            "type": "object",
            "properties": {
                "code": ONTOLOGY_CLASS,
                "body_site": ONTOLOGY_CLASS
            },
            "required": ["code"],
        },
        "hts_files": {
            "type": "array",
            "items": PHENOPACKET_HTS_FILE_SCHEMA
        },
        "variants": {
            "type": "array",
            "items": PHENOPACKET_VARIANT_SCHEMA
        },
        "is_control_sample": {
            "type": "boolean"
        },
        "measurements": {
            "type": "array",
            "items": PHENOPACKET_MEASUREMENT_SCHEMA
        },
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["id", "sampled_tissue", "procedure"],
}, descriptions.BIOSAMPLE)


PHENOPACKET_DISEASE_ONSET_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:disease_onset",
    "title": "Onset age",
    "description": "Schema for the age of the onset of the disease.",
    "type": "object",
    "anyOf": [
        AGE,
        AGE_RANGE,
        ONTOLOGY_CLASS
    ]
}

PHENOPACKET_DISEASE_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:disease",
    "title": "Disease schema",
    "type": "object",
    "properties": {
        "term": ONTOLOGY_CLASS,
        "onset": PHENOPACKET_DISEASE_ONSET_SCHEMA,
        "disease_stage": {
            "type": "array",
            "items": ONTOLOGY_CLASS,
        },
        "tnm_finding": {
            "type": "array",
            "items": ONTOLOGY_CLASS,
        },
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["term"],
}, descriptions.DISEASE)

# Deduplicate with other phenopacket representations
# noinspection PyProtectedMember
# PHENOPACKET_SCHEMA = tag_ids_and_describe({
#     "$schema": "http://json-schema.org/draft-07/schema#",
#     "$id": "katsu:phenopackets:phenopacket",
#     "title": "Phenopacket schema",
#     "description": "Schema for metadata service datasets",
#     "type": "object",
#     "properties": {
#         "id": {
#             "type": "string",
#         },
#         "subject": INDIVIDUAL_SCHEMA,
#         "phenotypic_features": {
#             "type": "array",
#             "items": PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA
#         },
#         "biosamples": {
#             "type": "array",
#             "items": PHENOPACKET_BIOSAMPLE_SCHEMA
#         },
#         "genes": {
#             "type": "array",
#             "items": PHENOPACKET_GENE_SCHEMA
#         },
#         "variants": {
#             "type": "array",
#             "items": PHENOPACKET_VARIANT_SCHEMA
#         },
#         "diseases": {  # TODO: Too sensitive for search?
#             "type": "array",
#             "items": PHENOPACKET_DISEASE_SCHEMA,
#         },  # TODO
#         "hts_files": {
#             "type": "array",
#             "items": PHENOPACKET_HTS_FILE_SCHEMA  # TODO
#         },
#         "meta_data": PHENOPACKET_META_DATA_SCHEMA,
#         "extra_properties": EXTRA_PROPERTIES_SCHEMA
#     },
#     "required": ["meta_data"],
# }, descriptions.PHENOPACKET)

PHENOPACKET_TREATMENT = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:treatment",
    "title": "Phenopacket treatment",
    "description": "Represents a treatment with an agent, such as a drug.",
    "type": "object",
    "properties": {
        "agent": ONTOLOGY_CLASS,
        "route_of_administration": ONTOLOGY_CLASS,
        "dose_intervals": {
            "type": "array",
            "items": {
                "quantity": PHENOPACKET_QUANTITY_SCHEMA,
                "schedule_frequency": ONTOLOGY_CLASS,
                "interval": TIME_INTERVAL
            }
        }
    }
}, {})

PHENOPACKET_RADIATION_THERAPY = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:radiation_therapy",
    "title": "Phenopacket radiation therapy",
    "description": "Radiation therapy (or radiotherapy) uses ionizing radiation, generally as part of cancer treatment to control or kill malignant cells.",
    "type": "object",
    "properties": {
        "modality": ONTOLOGY_CLASS,
        "body_site": ONTOLOGY_CLASS,
        "dosage": { "type": "integer" },
        "fractions": { "type": "integer" }
    },
    "required": ["modality", "body_site", "dosage", "fractions"]
}, {})

PHENOPACKET_THERAPEUTIC_REGIMEN = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:therapeutic_regimen",
    "title": "Phenopacket therapeutic regimen",
    "description": "This element represents a therapeutic regimen which will involve a specified set of treatments for a particular condition.",
    "type": "object",
    "properties": {
        "identifier": {
            "oneOf": [
                ONTOLOGY_CLASS,
                PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA
            ]
        },
        "start_time": PHENOPACKET_TIME_ELEMENT_SCHEMA,
        "end_time": PHENOPACKET_TIME_ELEMENT_SCHEMA,
        "status": { 
            "enum": ["UNKNOWN_STATUS", "STARTED", "COMPLETED", "DISCONTINUED"]
        }
    },
    "required": ["identifier", "status"]
}, {})

ONE_OF_MEDICAL_ACTION = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:one_of_medical_actions",
    "title": "Supported Phenopacket medical actions",
    "description": "One-of schema for supported medical action schemas",
    "type": "object",
    "oneOf": [
        PHENOPACKET_PROCEDURE_SCHEMA,
        PHENOPACKET_TREATMENT,
        PHENOPACKET_RADIATION_THERAPY,
        PHENOPACKET_THERAPEUTIC_REGIMEN
    ],
    "required": ["oneOf"]
}, {}) #TODO: describe

PHENOPACKET_MEDICAL_ACTION_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:medical_action",
    "title": "Phenopacket medical action schema",
    "description": "Describes a medical action",
    "type": "object",
    "properties": {
        "action": ONE_OF_MEDICAL_ACTION,
        "treatment_target": ONTOLOGY_CLASS,
        "treatment_intent": ONTOLOGY_CLASS,
        "response_to_treatment": ONTOLOGY_CLASS,
        "adverse_events": {
            "type": "array",
            "items": ONTOLOGY_CLASS
        },
        "treatment_termination_reason": ONTOLOGY_CLASS
    },
    "required": ["action"]
}, {})

PHENOPACKET_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:phenopackets:phenopacket",
    "title": "Phenopacket schema",
    "description": "Schema for metadata service datasets",
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
        },
        "subject": INDIVIDUAL_SCHEMA,
        "phenotypic_features": {
            "type": "array",
            "items": PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA
        },
        "biosamples": {
            "type": "array",
            "items": PHENOPACKET_BIOSAMPLE_SCHEMA
        },
        "genes": {
            "type": "array",
            "items": PHENOPACKET_GENE_SCHEMA
        },
        "variants": {
            "type": "array",
            "items": PHENOPACKET_VARIANT_SCHEMA
        },
        "diseases": {  # TODO: Too sensitive for search?
            "type": "array",
            "items": PHENOPACKET_DISEASE_SCHEMA,
        },  # TODO
        "hts_files": {
            "type": "array",
            "items": PHENOPACKET_HTS_FILE_SCHEMA  # TODO
        },
        "metaData": PHENOPACKET_META_DATA_SCHEMA,
        "measurements": {
            "type": "array",
            "items": PHENOPACKET_MEASUREMENT_SCHEMA
        },
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["metaData"],
}, descriptions.PHENOPACKET)
