# Individual schemas for validation of JSONField values

import chord_metadata_service.phenopackets.descriptions as descriptions
from chord_metadata_service.patients.descriptions import INDIVIDUAL
from chord_metadata_service.restapi.description_utils import describe_schema, ONTOLOGY_CLASS as ONTOLOGY_CLASS_DESC
from chord_metadata_service.restapi.schemas import AGE, AGE_RANGE, AGE_OR_AGE_RANGE, ONTOLOGY_CLASS


__all__ = [
    "ALLELE_SCHEMA",
    "PHENOPACKET_ONTOLOGY_SCHEMA",
    "PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA",
    "PHENOPACKET_INDIVIDUAL_SCHEMA",
    "PHENOPACKET_RESOURCE_SCHEMA",
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
]


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
        {"required": ["hgvs"]},
        {"required": ["genome_assembly"]},
        {"required": ["seq_id"]},
        {"required": ["iscn"]}
    ],
    "dependencies": {
        "genome_assembly": ["chr", "pos", "re", "alt", "info"],
        "seq_id": ["position", "deleted_sequence", "inserted_sequence"]
    }
}  # TODO: Descriptions


PHENOPACKET_ONTOLOGY_SCHEMA = describe_schema(ONTOLOGY_CLASS, ONTOLOGY_CLASS_DESC)

PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:external_reference_schema",
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


PHENOPACKET_INDIVIDUAL_SCHEMA = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "description": "Unique researcher-specified identifier for the individual.",
        },
        "alternate_ids": {
            "type": "array",
            "items": {
                "type": "string",
            },
            "description": "A list of alternative identifiers for the individual.",  # TODO: More specific
        },
        "date_of_birth": {
            # TODO: This is a special ISO format... need UI for this
            "type": "string",
        },
        "age": AGE_OR_AGE_RANGE,
        "sex": {
            "type": "string",
            "enum": ["UNKNOWN_SEX", "FEMALE", "MALE", "OTHER_SEX"],
            "description": "An individual's phenotypic sex.",
        },
        "karyotypic_sex": {
            "type": "string",
            "enum": [
                "UNKNOWN_KARYOTYPE",
                "XX",
                "XY",
                "XO",
                "XXY",
                "XXX",
                "XXYY",
                "XXXY",
                "XXXX",
                "XYY",
                "OTHER_KARYOTYPE"
            ],
            "description": "An individual's karyotypic sex.",
        },
        "taxonomy": PHENOPACKET_ONTOLOGY_SCHEMA,
    },
    "required": ["id"]
}, INDIVIDUAL)

PHENOPACKET_RESOURCE_SCHEMA = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",  # TODO
    "properties": {
        "id": {
            "type": "string",
        },
        "name": {
            "type": "string",
        },
        "namespace_prefix": {
            "type": "string",
        },
        "url": {
            "type": "string",
        },
        "version": {
            "type": "string",
        },
        "iri_prefix": {
            "type": "string",
        }
    },
    "required": ["id", "name", "namespace_prefix", "url", "version", "iri_prefix"],
}, descriptions.RESOURCE)


PHENOPACKET_UPDATE_SCHEMA = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:update_schema",
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
PHENOPACKET_META_DATA_SCHEMA = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
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
            "items": PHENOPACKET_RESOURCE_SCHEMA,
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
        }
    },
}, descriptions.META_DATA)

PHENOPACKET_EVIDENCE_SCHEMA = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:evidence_schema",
    "title": "Evidence schema",
    "type": "object",
    "properties": {
        "evidence_code": PHENOPACKET_ONTOLOGY_SCHEMA,
        "reference": PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA
    },
    "additionalProperties": False,
    "required": ["evidence_code"],
}, descriptions.EVIDENCE)

PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA = describe_schema({
    "type": "object",
    "properties": {
        "description": {
            "type": "string",
        },
        "type": PHENOPACKET_ONTOLOGY_SCHEMA,
        "negated": {
            "type": "boolean",
        },
        "severity": PHENOPACKET_ONTOLOGY_SCHEMA,
        "modifier": {  # TODO: Plural?
            "type": "array",
        },
        "onset": PHENOPACKET_ONTOLOGY_SCHEMA,
        "evidence": PHENOPACKET_EVIDENCE_SCHEMA,
    },
}, descriptions.PHENOTYPIC_FEATURE)


# TODO: search
PHENOPACKET_GENE_SCHEMA = describe_schema({
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
        }
    },
    "required": ["id", "symbol"]
}, descriptions.GENE)


PHENOPACKET_HTS_FILE_SCHEMA = describe_schema({
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
        }
    }
}, descriptions.HTS_FILE)


# TODO: search??
PHENOPACKET_VARIANT_SCHEMA = describe_schema({
    "type": "object",  # TODO
    "properties": {
        "allele": ALLELE_SCHEMA,  # TODO
        "zygosity": PHENOPACKET_ONTOLOGY_SCHEMA
    }
}, descriptions.VARIANT)

# noinspection PyProtectedMember
PHENOPACKET_BIOSAMPLE_SCHEMA = describe_schema({
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
        "sampled_tissue": PHENOPACKET_ONTOLOGY_SCHEMA,
        "phenotypic_features": {
            "type": "array",
            "items": PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA,
        },
        "taxonomy": PHENOPACKET_ONTOLOGY_SCHEMA,
        "individual_age_at_collection": AGE_OR_AGE_RANGE,
        "histological_diagnosis": PHENOPACKET_ONTOLOGY_SCHEMA,
        "tumor_progression": PHENOPACKET_ONTOLOGY_SCHEMA,
        "tumor_grade": PHENOPACKET_ONTOLOGY_SCHEMA,  # TODO: Is this a list?
        "diagnostic_markers": {
            "type": "array",
            "items": PHENOPACKET_ONTOLOGY_SCHEMA,
        },
        "procedure": {
            "type": "object",
            "properties": {
                "code": PHENOPACKET_ONTOLOGY_SCHEMA,
                "body_site": PHENOPACKET_ONTOLOGY_SCHEMA
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
    },
    "required": ["id", "sampled_tissue", "procedure"],
}, descriptions.BIOSAMPLE)


PHENOPACKET_DISEASE_ONSET_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:disease_onset_schema",
    "title": "Onset age",
    "description": "Schema for the age of the onset of the disease.",
    "type": "object",
    "anyOf": [
        AGE,
        AGE_RANGE,
        PHENOPACKET_ONTOLOGY_SCHEMA
    ]
}

PHENOPACKET_DISEASE_SCHEMA = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:disease_schema",
    "title": "Disease schema",
    "type": "object",
    "properties": {
        "term": PHENOPACKET_ONTOLOGY_SCHEMA,
        "onset": PHENOPACKET_DISEASE_ONSET_SCHEMA,
        "disease_stage": {
            "type": "array",
            "items": PHENOPACKET_ONTOLOGY_SCHEMA,
        },
        "tnm_finding": {
            "type": "array",
            "items": PHENOPACKET_ONTOLOGY_SCHEMA,
        },
    },
    "required": ["term"],
}, descriptions.DISEASE)

# Deduplicate with other phenopacket representations
# noinspection PyProtectedMember
PHENOPACKET_SCHEMA = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:phenopacket_schema",
    "title": "Phenopacket schema",
    "description": "Schema for metadata service datasets",
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
        },
        "subject": PHENOPACKET_INDIVIDUAL_SCHEMA,
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
        "meta_data": PHENOPACKET_META_DATA_SCHEMA
    },
    "required": ["id", "meta_data"],
}, descriptions.PHENOPACKET)
