# Individual schemas for validation of JSONField values

import chord_metadata_service.phenopackets.descriptions as descriptions
from chord_metadata_service.phenopackets.models import *
from chord_metadata_service.patients.descriptions import INDIVIDUAL
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.restapi.description_utils import describe_schema, ONTOLOGY_CLASS

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
        {"required": ["hgvs"]},
        {"required": ["genome_assembly"]},
        {"required": ["seq_id"]},
        {"required": ["iscn"]}
    ],
    "dependencies": {
        "genome_assembly": ["chr", "pos", "re", "alt", "info"],
        "seq_id": ["position", "deleted_sequence", "inserted_sequence"]
    }
}


UPDATE_SCHEMA = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "todo",
    "title": "Updates schema",
    "description": "Schema to check incoming updates format",
    "type": "object",
    "properties": {
        "timestamp": {
            "type": "string",
            "format": "date-time",
        },
        "updated_by": {"type": "string"},
        "comment": {"type": "string"}
    },
    "required": ["timestamp", "comment"]
}, descriptions.UPDATE)


def _single_optional_eq_search(order, queryable: str = "all"):
    return {
        "operations": ["eq"],
        "queryable": queryable,
        "canNegate": True,
        "required": False,
        "type": "single",
        "order": order
    }


def _optional_str_search(order, queryable: str = "all"):
    return {
        "operations": ["eq", "co"],
        "queryable": queryable,
        "canNegate": True,
        "required": False,
        "order": order
    }


def _single_optional_str_search(order, queryable: str = "all"):
    return {**_optional_str_search(order, queryable), "type": "single"}


def _multiple_optional_str_search(order, queryable: str = "all"):
    return {**_optional_str_search(order, queryable), "type": "multiple"}


def _tag_with_database_attrs(schema: dict, db_attrs: dict):
    return {
        **schema,
        "search": {
            **schema.get("search", {}),
            "database": {
                **schema.get("search", {}).get("database", {}),
                **db_attrs
            }
        }
    }


PHENOPACKET_ONTOLOGY_SCHEMA = describe_schema({
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "search": _multiple_optional_str_search(0)
        },
        "label": {
            "type": "string",
            "search": _multiple_optional_str_search(1)
        },
    },
    "required": ["id", "label"],
    "search": {
        "database": {
            "type": "jsonb"  # TODO: parameterize?
        }
    }
}, ONTOLOGY_CLASS)

PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA = describe_schema({
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "search": _single_optional_str_search(0)
        },
        "description": {
            "type": "string",
            "search": _multiple_optional_str_search(1)  # TODO: Searchable? may leak
        }
    },
    "required": ["id"],
    "search": {
        "database": {
            "type": "jsonb"  # TODO: parameterize?
        }
    }
}, descriptions.EXTERNAL_REFERENCE)


PHENOPACKET_INDIVIDUAL_SCHEMA = describe_schema({
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "description": "Unique researcher-specified identifier for the individual.",
            "search": {
                **_single_optional_eq_search(0, queryable="internal"),
                "database": {
                    "field": Individual._meta.pk.column
                }
            }
        },
        "alternate_ids": {
            "type": "array",
            "items": {
                "type": "string",
                "search": _multiple_optional_str_search(0, queryable="internal")
            },
            "description": "A list of alternative identifiers for the individual.",  # TODO: More specific
            "search": {
                "database": {
                    "type": "array"
                }
            }
        },
        "date_of_birth": {
            # TODO: This is a special ISO format... need UI for this
            # TODO: Internal?
            "type": "string",
            "search": _single_optional_eq_search(1, queryable="internal")
        },
        # TODO: Age
        "sex": {
            "type": "string",
            "enum": ["UNKNOWN_SEX", "FEMALE", "MALE", "OTHER_SEX"],
            "description": "An individual's phenotypic sex.",
            "search": _single_optional_eq_search(2)
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
            "search": _single_optional_eq_search(3)
        },
        "taxonomy": PHENOPACKET_ONTOLOGY_SCHEMA,
    },
    "search": {
        "database": {
            "relation": Individual._meta.db_table,
            "primary_key": Individual._meta.pk.column,
        }
    },
    "required": ["id"]
}, INDIVIDUAL)

PHENOPACKET_RESOURCE_SCHEMA = describe_schema({
    "type": "object",  # TODO
    "properties": {
        "id": {
            "type": "string",
            "search": _single_optional_str_search(0)
        },
        "name": {
            "type": "string",
            "search": _multiple_optional_str_search(1)
        },
        "namespace_prefix": {
            "type": "string",
            "search": _multiple_optional_str_search(2)
        },
        "url": {
            "type": "string",
            "search": _multiple_optional_str_search(3)
        },
        "version": {
            "type": "string",
            "search": _multiple_optional_str_search(4)
        },
        "iri_prefix": {
            "type": "string",
            "search": _multiple_optional_str_search(5)
        }
    },
    "required": ["id", "name", "namespace_prefix", "url", "version", "iri_prefix"],
    "search": {
        "database": {
            "relationship": {
                "type": "MANY_TO_ONE",
                "foreign_key": "resource_id"  # TODO: No hard-code, from M2M
            }
        }
    }
}, descriptions.RESOURCE)


PHENOPACKET_UPDATE_SCHEMA = describe_schema({
    "type": "object",  # TODO
    "properties": {
        "timestamp": {
            "type": "string",
        },
        "updated_by": {
            "type": "string",
            "search": _multiple_optional_str_search(0),
        },
        "comment": {
            "type": "string",
            "search": _multiple_optional_str_search(1)
        }
    },
    "required": ["timestamp", "comment"],
    "search": {
        "database": {
            "type": "jsonb"
        }
    }
}, descriptions.UPDATE)


# noinspection PyProtectedMember
PHENOPACKET_META_DATA_SCHEMA = describe_schema({
    "type": "object",
    "properties": {
        "created": {"type": "string"},
        "created_by": {
            "type": "string",
            "search": _multiple_optional_str_search(0)
        },
        "submitted_by": {
            "type": "string",
            "search": _multiple_optional_str_search(1)
        },
        "resources": {
            "type": "array",
            "items": PHENOPACKET_RESOURCE_SCHEMA,
            "search": {
                "database": {
                    "relation": MetaData._meta.get_field("resources").remote_field.through._meta.db_table,
                    "relationship": {
                        "type": "ONE_TO_MANY",
                        "parent_foreign_key": "metadata_id",  # TODO: No hard-code
                        "parent_primary_key": MetaData._meta.pk.column  # TODO: Redundant?
                    }
                }
            }
        },
        "updates": {
            "type": "array",
            "items": PHENOPACKET_UPDATE_SCHEMA,
            "search": {
                "database": {
                    "type": "array"
                }
            }
        },
        "phenopacket_schema_version": {
            "type": "string",
        },
        "external_references": {
            "type": "array",
            "items": PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA
        }
    },
    "search": {
        "database": {
            "relation": MetaData._meta.db_table,
            "primary_key": MetaData._meta.pk.column
        }
    }
}, descriptions.META_DATA)

PHENOPACKET_EVIDENCE_SCHEMA = describe_schema({
    "type": "object",
    "properties": {
        "evidence_code": PHENOPACKET_ONTOLOGY_SCHEMA,
        "reference": PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA
    },
    "required": ["evidence_code"],
    "search": {
        "database": {
            "type": "jsonb"
        }
    }
}, descriptions.EVIDENCE)

PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA = describe_schema({
    "type": "object",
    "properties": {
        "description": {
            "type": "string",
            "search": _multiple_optional_str_search(0),  # TODO: Searchable? may leak
        },
        "type": PHENOPACKET_ONTOLOGY_SCHEMA,
        "negated": {
            "type": "boolean",
            "search": _single_optional_eq_search(1)
        },
        "severity": PHENOPACKET_ONTOLOGY_SCHEMA,
        "modifier": {  # TODO: Plural?
            "type": "array",
            "items": PHENOPACKET_ONTOLOGY_SCHEMA
        },
        "onset": PHENOPACKET_ONTOLOGY_SCHEMA,
        "evidence": PHENOPACKET_EVIDENCE_SCHEMA,
    },
    "search": {
        "database": {
            "relation": PhenotypicFeature._meta.db_table,
            "primary_key": PhenotypicFeature._meta.pk.column
        }
    }
}, descriptions.PHENOTYPIC_FEATURE)

PHENOPACKET_AGE_SCHEMA = describe_schema({
    "type": "object",
    "properties": {
        "age": {
            "type": "string",
        }
    },
    "required": ["age"]
}, descriptions.AGE_NESTED)


# TODO: search
PHENOPACKET_GENE_SCHEMA = describe_schema({
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
}, descriptions.GENE)


PHENOPACKET_HTS_FILE_SCHEMA = describe_schema({
    # TODO: Search? Probably not
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
            "search": {
                **_single_optional_eq_search(0, queryable="internal"),
                "database": {"field": Biosample._meta.pk.column}
            }
        },
        "individual_id": {
            "type": "string",
        },
        "description": {
            "type": "string",
            "search": _multiple_optional_str_search(1),  # TODO: Searchable? may leak
        },
        "sampled_tissue": PHENOPACKET_ONTOLOGY_SCHEMA,
        "phenotypic_features": {
            "type": "array",
            "items": PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA,
            "search": {
                "database": {
                    **PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA["search"]["database"],
                    "relationship": {
                        "type": "ONE_TO_MANY",
                        "parent_foreign_key": PhenotypicFeature._meta.get_field("biosample").column,
                        "parent_primary_key": Biosample._meta.pk.column  # TODO: Redundant
                    }
                }
            }
        },
        "taxonomy": PHENOPACKET_ONTOLOGY_SCHEMA,
        "individual_age_at_collection": {
            "type": "object",
            "oneOf": [  # TODO: Front end will need to deal with this
                {
                    "properties": PHENOPACKET_AGE_SCHEMA["properties"],
                    "description": PHENOPACKET_AGE_SCHEMA["description"],
                    "required": ["age"],
                    "additionalProperties": False
                },
                {
                    "properties": {
                        "start": PHENOPACKET_AGE_SCHEMA,
                        "end": PHENOPACKET_AGE_SCHEMA,
                    },
                    "description": d.AGE_RANGE,  # TODO: annotated
                    "required": ["start", "end"],
                    "additionalProperties": False
                }
            ]
        },
        "histological_diagnosis": PHENOPACKET_ONTOLOGY_SCHEMA,
        "tumor_progression": PHENOPACKET_ONTOLOGY_SCHEMA,
        "tumor_grade": PHENOPACKET_ONTOLOGY_SCHEMA,  # TODO: Is this a list?
        "diagnostic_markers": {
            "type": "array",
            "items": PHENOPACKET_ONTOLOGY_SCHEMA,
            "search": {"database": {"type": "array"}}
        },
        "procedure": {
            "type": "object",
            "properties": {
                "code": PHENOPACKET_ONTOLOGY_SCHEMA,
                "body_site": PHENOPACKET_ONTOLOGY_SCHEMA
            },
            "required": ["code"],
            "search": {
                "database": {
                    "primary_key": Procedure._meta.pk.column,
                    "relation": Procedure._meta.db_table,
                    "relationship": {
                        "type": "MANY_TO_ONE",
                        "foreign_key": Biosample._meta.get_field("procedure").column
                    }
                }
            }
        },
        "hts_files": {
            "type": "array",
            "items": PHENOPACKET_HTS_FILE_SCHEMA  # TODO
        },
        "variants": {
            "type": "array",
            "items": PHENOPACKET_VARIANT_SCHEMA,  # TODO: search?
        },
        "is_control_sample": {
            "type": "boolean",  # TODO: Boolean search
            "search": _single_optional_eq_search(1),
        },
    },
    "required": ["id", "sampled_tissue", "procedure"],
    "search": {
        "database": {
            "primary_key": Biosample._meta.pk.column,
            "relation": Biosample._meta.db_table,
        }
    }
}, descriptions.BIOSAMPLE)

PHENOPACKET_DISEASE_SCHEMA = describe_schema({
    "type": "object",
    "properties": {
        "term": PHENOPACKET_ONTOLOGY_SCHEMA,
        "onset": PHENOPACKET_AGE_SCHEMA,
        "disease_stage": {
            "type": "array",
            "items": PHENOPACKET_ONTOLOGY_SCHEMA,
            "search": {"database": {"type": "array"}}
        },
        "tnm_finding": {
            "type": "array",
            "items": PHENOPACKET_ONTOLOGY_SCHEMA,
            "search": {"database": {"type": "array"}}
        },
    },
    "required": ["term"],
    "search": {
        "database": {
            "primary_key": Disease._meta.pk.column,
            "relation": Disease._meta.db_table,
        }
    }
}, descriptions.DISEASE)

# Deduplicate with other phenopacket representations
# noinspection PyProtectedMember
PHENOPACKET_SCHEMA = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "TODO",
    "title": "Dataset Table Schema",
    "description": "Schema for metadata service datasets",
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "search": {"database": {"field": Phenopacket._meta.pk.column}}
        },
        "subject": _tag_with_database_attrs(PHENOPACKET_INDIVIDUAL_SCHEMA, {
            "relationship": {
                "type": "MANY_TO_ONE",
                "foreign_key": Phenopacket._meta.get_field("subject").column
            }
        }),
        "phenotypic_features": {
            "type": "array",
            "items": PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA,
            "search": {
                "database": {
                    **PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA["search"]["database"],
                    "relationship": {
                        "type": "ONE_TO_MANY",
                        "parent_foreign_key": "phenopacket_id",  # TODO: No hard-code
                        "parent_primary_key": Phenopacket._meta.pk.column  # TODO: Redundant?
                    }
                }
            }
        },
        "biosamples": {
            "type": "array",
            "items": {
                **PHENOPACKET_BIOSAMPLE_SCHEMA,
                "search": {
                    "database": {
                        **PHENOPACKET_BIOSAMPLE_SCHEMA["search"]["database"],
                        "relationship": {
                            "type": "MANY_TO_ONE",
                            "foreign_key": "biosample_id"  # TODO: No hard-code, from M2M
                        }
                    }
                }
            },
            "search": {
                "database": {
                    "relation": Phenopacket._meta.get_field("biosamples").remote_field.through._meta.db_table,
                    "relationship": {
                        "type": "ONE_TO_MANY",
                        "parent_foreign_key": "phenopacket_id",  # TODO: No hard-code
                        "parent_primary_key": Phenopacket._meta.pk.column  # TODO: Redundant?
                    }
                }
            }
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
            "items": {
                **PHENOPACKET_DISEASE_SCHEMA,
                "search": {
                    **PHENOPACKET_DISEASE_SCHEMA["search"],
                    "database": {
                        **PHENOPACKET_DISEASE_SCHEMA["search"]["database"],
                        "relationship": {
                            "type": "MANY_TO_ONE",
                            "foreign_key": "disease_id"  # TODO: No hard-code, from M2M
                        }
                    }
                }
            },
            "search": {
                "database": {
                    "relation": Phenopacket._meta.get_field("diseases").remote_field.through._meta.db_table,
                    "relationship": {
                        "type": "ONE_TO_MANY",
                        "parent_foreign_key": "phenopacket_id",  # TODO: No hard-code
                        "parent_primary_key": Phenopacket._meta.pk.column  # TODO: Redundant?
                    }
                }
            }
        },  # TODO
        "hts_files": {
            "type": "array",
            "items": PHENOPACKET_HTS_FILE_SCHEMA  # TODO
        },
        "meta_data": PHENOPACKET_META_DATA_SCHEMA
    },
    "required": ["id", "meta_data"],
    "search": {
        "database": {
            "relation": Phenopacket._meta.db_table,
            "primary_key": Phenopacket._meta.pk.column
        }
    }
}, descriptions.PHENOPACKET)
