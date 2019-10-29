# Individual schemas for validation of JSONField values

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
        "timestamp": {
            "type": "string",
            "format": "date-time",
            "description": "ISO8601 UTC timestamp at which this record was updated"
        },
        "updated_by": {"type": "string", "description": "Who updated the phenopacket"},
        "comment": {"type": "string", "description": "Comment about updates or reasons for an update"}
    },
    "required": ["timestamp", "comment"]
}


def _single_optional_eq_search(order):
    return {
        "operations": ["eq"],
        "canNegate": True,
        "required": False,
        "type": "single",
        "order": order
    }


def _single_optional_str_search(order):
    return {
        "operations": ["eq", "co"],
        "canNegate": True,
        "required": False,
        "type": "single",
        "order": order
    }


PHENOPACKET_ONTOLOGY_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "search": _single_optional_str_search(0)
        },
        "label": {
            "type": "string",
            "search": _single_optional_str_search(1)
        },
    },
    "required": ["id", "label"]
}

PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "search": _single_optional_str_search(0)
        },
        "description": {
            "type": "string",
            "search": _single_optional_str_search(1)
        }
    },
    "required": ["id"]
}


PHENOPACKET_INDIVIDUAL_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {
            "type": "string"
        },
        "alternate_ids": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "date_of_birth": {
            "type": "string"
        },
        # TODO: Age
        "sex": {  # TODO: Front end: enum dropdown
            "type": "string",
            "enum": ["UNKNOWN_SEX", "FEMALE", "MALE", "OTHER_SEX"],
            "search": _single_optional_eq_search(0)
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
            "search": _single_optional_eq_search(1)
        },
        "taxonomy": PHENOPACKET_ONTOLOGY_SCHEMA
    },
    "required": ["id"]
}

PHENOPACKET_META_DATA_SCHEMA = {
    "type": "object",
    "properties": {
        "created": {"type": "string"},
        "created_by": {
            "type": "string",
            "search": _single_optional_str_search(0)
        },
        "submitted_by": {
            "type": "string",
            "search": _single_optional_str_search(1)
        },
        "resources": {
            "type": "array",
            "items": {
                "type": "object",  # TODO
                "properties": {
                    "id": {"type": "string"},
                    "name": {
                        "type": "string",
                        "search": _single_optional_str_search(0)
                    },
                    "namespace_prefix": {"type": "string"},
                    "url": {"type": "string"},
                    "version": {"type": "string"},
                    "iri_prefix": {"type": "string"}
                },
                "required": ["id", "name", "namespace_prefix", "url", "version", "iri_prefix"]
            }
        },
        "updates": {
            "type": "array",
            "items": {
                "type": "object",  # TODO
                "properties": {
                    "timestamp": {
                        "type": "string"
                    },
                    "updated_by": {
                        "type": "string"
                    },
                    "comment": {
                        "type": "string"
                    }
                },
                "required": ["timestamp", "comment"]
            }
        },
        "phenopacket_schema_version": {
            "type": "string"
        },
        "external_references": {
            "type": "array",
            "items": PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA
        }
    }
}

PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA = {
    "type": "object",
    "properties": {
        "description": {
            "type": "string"
        },
        "type": PHENOPACKET_ONTOLOGY_SCHEMA,
        "negated": {
            "type": "boolean"
        },
        "severity": PHENOPACKET_ONTOLOGY_SCHEMA,
        "modifiers": {  # TODO: Plural?
            "type": "array",
            "items": PHENOPACKET_ONTOLOGY_SCHEMA
        },
        "onset": PHENOPACKET_ONTOLOGY_SCHEMA,
        "evidence": {
            "type": "object",
            "properties": {
                "evidence_code": PHENOPACKET_ONTOLOGY_SCHEMA,
                "reference": PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA
            },
            "required": ["evidence_code"]
        }
    }
}

PHENOPACKET_AGE_SCHEMA = {
    "type": "object",
    "properties": {
        "age": {"type": "string"}
    }
}

PHENOPACKET_BIOSAMPLE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "individual_id": {"type": "string"},
        "description": {"type": "string"},
        "sampled_tissue": PHENOPACKET_ONTOLOGY_SCHEMA,
        "phenotypic_features": {
            "type": "array",
            "items": PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA
        },
        "taxonomy": PHENOPACKET_ONTOLOGY_SCHEMA,
        "individual_age_at_collection": {
            "type": "object",
            "oneOf": [  # TODO: Front end will need to deal with this
                {"properties": PHENOPACKET_AGE_SCHEMA["properties"]},
                {"properties": {
                    "start": PHENOPACKET_AGE_SCHEMA,
                    "end": PHENOPACKET_AGE_SCHEMA
                }}
            ]
        },
        "histological_diagnosis": PHENOPACKET_ONTOLOGY_SCHEMA,
        "tumor_progression": PHENOPACKET_ONTOLOGY_SCHEMA,
        "tumor_grade": {
            "type": "array",
            "items": PHENOPACKET_ONTOLOGY_SCHEMA
        },
        "diagnostic_markers": {
            "type": "array",
            "items": PHENOPACKET_ONTOLOGY_SCHEMA
        },
        "procedure": {
            "type": "object",
            "properties": {
                "code": PHENOPACKET_ONTOLOGY_SCHEMA,
                "body_site": PHENOPACKET_ONTOLOGY_SCHEMA
            },
            "required": ["code"]
        },
        "hts_files": {
            "type": "array",
            "items": {
                "type": "object"  # TODO
            }
        },
        "variants": {
            "type": "array",
            "items": {
                "type": "object"  # TODO
            }
        },
        "is_control_sample": {
            "type": "boolean"  # TODO: Boolean search
        },
    },
    "required": ["id", "sampled_tissue", "procedure"]
}

# Deduplicate with other phenopacket representations
PHENOPACKET_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "TODO",
    "title": "Dataset Table Schema",
    "description": "Schema for metadata service datasets",
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "search": {"database": {"field": "phenopacket_id"}}
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
            "items": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "search": _single_optional_str_search(0)
                    },
                    "alternate_ids": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "search": _single_optional_str_search(1)
                        }
                    },
                    "symbol": {
                        "type": "string",
                        "search": _single_optional_str_search(2)
                    }
                },
                "required": ["id", "symbol"]
            }
        },
        "variants": {
            "type": "array",
            "items": {
                "type": "object"  # TODO
            }
        },
        "diseases": {  # TODO: Too sensitive for search?
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "allele": {"type": "object"},  # TODO
                    "zygosity": PHENOPACKET_ONTOLOGY_SCHEMA
                },
                "required": ["allele"]
            }
        },  # TODO
        "hts_files": {
            "type": "array",
            "items": {
                "type": "object"  # TODO
            }
        },
        "meta_data": PHENOPACKET_META_DATA_SCHEMA
    },
    "required": ["id", "meta_data"],
    "search": {
        "database": {
            "relation": "patients_phenopacket",
            "primary_key": "phenopacket_id"
        }
    }
}
