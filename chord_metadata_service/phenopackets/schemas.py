# Individual schemas for validation of JSONField values

from chord_metadata_service.phenopackets.models import *
from chord_metadata_service.patients.models import Individual

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


PHENOPACKET_ONTOLOGY_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "description": "A CURIE-formatted ontology term, e.g. NCIT:C15189.",
            "search": _multiple_optional_str_search(0)
        },
        "label": {
            "type": "string",
            "description": "A human-readable label for the ontology term, e.g. Biopsy.",
            "search": _multiple_optional_str_search(1)
        },
    },
    "required": ["id", "label"],
    "search": {
        "database": {
            "type": "jsonb"  # TODO: parameterize?
        }
    }
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
            "search": _multiple_optional_str_search(1)  # TODO: Searchable? may leak
        }
    },
    "required": ["id"],
    "search": {
        "database": {
            "type": "jsonb"  # TODO: parameterize?
        }
    }
}


def phenopacket_individual_schema(database_attrs: dict):
    return {
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
                **database_attrs
            }
        },
        "required": ["id"]
    }


# noinspection PyProtectedMember
PHENOPACKET_META_DATA_SCHEMA = {
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
            "items": {
                "type": "object",  # TODO
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Unique researcher-specified identifier for the resource",  # TODO: specified?
                        "search": _single_optional_str_search(0)
                    },
                    "name": {
                        "type": "string",
                        "description": "Human-readable name for the resource",
                        "search": _multiple_optional_str_search(1)
                    },
                    "namespace_prefix": {
                        "type": "string",
                        "description": "Prefix for objects from this resource",
                        "search": _multiple_optional_str_search(2)
                    },
                    "url": {
                        "type": "string",
                        "description": "Resource URL (In the case of ontologies, should be an OBO or OWL file)",
                        "search": _multiple_optional_str_search(3)
                    },
                    "version": {
                        "type": "string",
                        "description": "Arbitrary resource version",
                        "search": _multiple_optional_str_search(4)
                    },
                    "iri_prefix": {
                        "type": "string",
                        "description": ("The IRI prefix, when used with the namespace prefix and an object ID, should "
                                        "resolve the term or object from the resource in question."),
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
            },
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
            "items": {
                "type": "object",  # TODO
                "properties": {
                    "timestamp": {
                        "type": "string",
                        "description": "ISO8601 timestamp containing the time the update was made"
                    },
                    "updated_by": {
                        "type": "string",
                        "description": "Who performed the update",
                        "search": _multiple_optional_str_search(0),
                    },
                    "comment": {
                        "type": "string",
                        "description": "Human-readable text describing the content or reason for the update",
                        "search": _multiple_optional_str_search(1)
                    }
                },
                "required": ["timestamp", "comment"],
                "search": {
                    "database": {
                        "type": "jsonb"
                    }
                }
            },
            "search": {
                "database": {
                    "type": "array"
                }
            }
        },
        "phenopacket_schema_version": {
            "type": "string"
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
}

PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA = {
    "type": "object",
    "properties": {
        "description": {
            "type": "string",
            "description": "Human-readable text describing the phenotypic feature",
            "search": _multiple_optional_str_search(0),  # TODO: Searchable? may leak
        },
        "type": PHENOPACKET_ONTOLOGY_SCHEMA,
        "negated": {
            "type": "boolean",
            "description": "Whether the feature is present (false) or absent (true, feature is negated)",
            "search": _single_optional_eq_search(1)
        },
        "severity": {
            **PHENOPACKET_ONTOLOGY_SCHEMA,
            "description": "Ontology term describing the severity of the phenotype"
        },
        "modifiers": {  # TODO: Plural?
            "type": "array",  # TODO: Description
            "items": PHENOPACKET_ONTOLOGY_SCHEMA
        },
        "onset": {
            **PHENOPACKET_ONTOLOGY_SCHEMA,
            "description": "Ontology term describing the onset of the phenotype"
        },
        "evidence": {
            "type": "object",
            "description": "Evidence for the assertion of the observation of the phenotypic feature type",
            "properties": {
                "evidence_code": {
                    **PHENOPACKET_ONTOLOGY_SCHEMA,
                    "description": "Ontology term representing the evidence type"
                },
                "reference": {
                    **PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA,
                    "description": "Source of the evidence"
                }
            },
            "required": ["evidence_code"],
            "search": {
                "database": {
                    "type": "jsonb"
                }
            }
        }
    },
    "search": {
        "database": {
            "relation": PhenotypicFeature._meta.db_table,
            "primary_key": PhenotypicFeature._meta.pk.column
        }
    }
}

PHENOPACKET_AGE_SCHEMA = {
    "type": "object",
    "properties": {
        "age": {
            "type": "string",
            "description": ("An ISO8601 duration string (e.g. P40Y10M05D for 40 years, 10 months, 5 days) representing "
                            "an age of a subject")
        }
    },
    "required": ["age"]
}

# noinspection PyProtectedMember
PHENOPACKET_BIOSAMPLE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "description": "Unique researcher-specified identifier for the biosample.",
            "search": {
                **_single_optional_eq_search(0, queryable="internal"),
                "database": {"field": Biosample._meta.pk.column}
            }
        },
        "individual_id": {
            "type": "string",
            "description": "Identifier for the individual this biosample was sampled from."
        },
        "description": {
            "type": "string",
            "description": "Researcher-specified free text field to describe the biosample.",
            "search": _multiple_optional_str_search(1),  # TODO: Searchable? may leak
        },
        "sampled_tissue": PHENOPACKET_ONTOLOGY_SCHEMA,
        "phenotypic_features": {
            "type": "array",
            "items": PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA,
            "description": "A list of phenotypic features associated with the biosample.",  # TODO: More specific
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
                    "description": "Age range (e.g. when a subject's age falls into a bin)",
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
}

# Deduplicate with other phenopacket representations
# noinspection PyProtectedMember
PHENOPACKET_SCHEMA = {
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
        "subject": phenopacket_individual_schema({
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
                "type": "object",  # TODO
                "properties": {
                    "allele": ALLELE_SCHEMA,  # TODO
                    "zygosity": PHENOPACKET_ONTOLOGY_SCHEMA
                }
            }
        },
        "diseases": {  # TODO: Too sensitive for search?
            "type": "array",
            "items": {
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
            "items": {
                "type": "object"  # TODO
            }
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
}
