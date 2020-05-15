from . import models, schemas
from chord_metadata_service.patients.schemas import INDIVIDUAL_SCHEMA
from chord_metadata_service.restapi.schema_utils import tag_schema_with_search_properties


__all__ = [
    "ONTOLOGY_SEARCH_SCHEMA",
    "EXTERNAL_REFERENCE_SEARCH_SCHEMA",
    "PHENOPACKET_SEARCH_SCHEMA",
]


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


# TODO: Rewrite and use
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


ONTOLOGY_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_ONTOLOGY_SCHEMA, {
    "properties": {
        "id": {
            "search": _multiple_optional_str_search(0)
        },
        "label": {
            "search": _multiple_optional_str_search(1)
        }
    },
    "search": {
        "database": {
            "type": "jsonb"  # TODO: parameterize?
        }
    }
})

EXTERNAL_REFERENCE_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA, {
    "properties": {
        "id": {
            "search": _single_optional_str_search(0)
        },
        "description": {
            "search": _multiple_optional_str_search(1)  # TODO: Searchable? may leak
        }
    },
    "search": {
        "database": {
            "type": "jsonb"  # TODO: parameterize?
        }
    }
})

INDIVIDUAL_SEARCH_SCHEMA = tag_schema_with_search_properties(INDIVIDUAL_SCHEMA, {
    "properties": {
        "id": {
            "search": {
                **_single_optional_eq_search(0, queryable="internal"),
                "database": {
                    "field": models.Individual._meta.pk.column
                }
            }
        },
        "alternate_ids": {
            "items": {
                "search": _multiple_optional_str_search(0, queryable="internal")
            },
            "search": {
                "database": {
                    "type": "array"
                }
            }
        },
        "date_of_birth": {
            # TODO: Internal?
            "search": _single_optional_eq_search(1, queryable="internal")
        },
        # TODO: Age
        "sex": {
            "search": _single_optional_eq_search(2)
        },
        "karyotypic_sex": {
            "search": _single_optional_eq_search(3)
        },
        "taxonomy": ONTOLOGY_SEARCH_SCHEMA,
    },
    "search": {
        "database": {
            "relation": models.Individual._meta.db_table,
            "primary_key": models.Individual._meta.pk.column,
        }
    },
})

RESOURCE_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_RESOURCE_SCHEMA, {
    "properties": {
        "id": {
            "search": _single_optional_str_search(0)
        },
        "name": {
            "search": _multiple_optional_str_search(1)
        },
        "namespace_prefix": {
            "search": _multiple_optional_str_search(2)
        },
        "url": {
            "search": _multiple_optional_str_search(3)
        },
        "version": {
            "search": _multiple_optional_str_search(4)
        },
        "iri_prefix": {
            "search": _multiple_optional_str_search(5)
        }
    },
    "search": {
        "database": {
            "relationship": {
                "type": "MANY_TO_ONE",
                "foreign_key": "resource_id"  # TODO: No hard-code, from M2M
            }
        }
    }
})

UPDATE_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_UPDATE_SCHEMA, {
    "properties": {
        # TODO: timestamp
        "updated_by": {
            "search": _multiple_optional_str_search(0),
        },
        "comment": {
            "search": _multiple_optional_str_search(1)
        }
    },
    "search": {
        "database": {
            "type": "jsonb"
        }
    }
})

# noinspection PyProtectedMember
META_DATA_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_META_DATA_SCHEMA, {
    "properties": {
        # TODO: created
        "created_by": {
            "search": _multiple_optional_str_search(0)
        },
        "submitted_by": {
            "search": _multiple_optional_str_search(1)
        },
        "resources": {
            "items": RESOURCE_SEARCH_SCHEMA,
            "search": {
                "database": {
                    "relation": models.MetaData._meta.get_field("resources").remote_field.through._meta.db_table,
                    "relationship": {
                        "type": "ONE_TO_MANY",
                        "parent_foreign_key": "metadata_id",  # TODO: No hard-code
                        "parent_primary_key": models.MetaData._meta.pk.column  # TODO: Redundant?
                    }
                }
            }
        },
        "updates": {
            "items": UPDATE_SEARCH_SCHEMA,
            "search": {
                "database": {
                    "type": "array"
                }
            }
        },
        # TODO: phenopacket_schema_version
        "external_references": {
            "items": EXTERNAL_REFERENCE_SEARCH_SCHEMA
        }
    },
    "search": {
        "database": {
            "relation": models.MetaData._meta.db_table,
            "primary_key": models.MetaData._meta.pk.column
        }
    }
})

EVIDENCE_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_EVIDENCE_SCHEMA, {
    "properties": {
        "evidence_code": ONTOLOGY_SEARCH_SCHEMA,
        "reference": EXTERNAL_REFERENCE_SEARCH_SCHEMA,
    },
    "search": {
        "database": {
            "type": "jsonb"
        }
    }
})

PHENOTYPIC_FEATURE_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA, {
    "properties": {
        "description": {
            "search": _multiple_optional_str_search(0),  # TODO: Searchable? may leak
        },
        "type": ONTOLOGY_SEARCH_SCHEMA,
        "negated": {
            "search": _single_optional_eq_search(1)
        },
        "severity": ONTOLOGY_SEARCH_SCHEMA,
        "modifier": {  # TODO: Plural?
            "items": ONTOLOGY_SEARCH_SCHEMA
        },
        "onset": ONTOLOGY_SEARCH_SCHEMA,
        "evidence": EVIDENCE_SEARCH_SCHEMA,
    },
    "search": {
        "database": {
            "relation": models.PhenotypicFeature._meta.db_table,
            "primary_key": models.PhenotypicFeature._meta.pk.column
        }
    }
})

# TODO: Fix
GENE_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_GENE_SCHEMA, {
    "properties": {
        "id": {
            "search": _single_optional_str_search(0)
        },
        "alternate_ids": {
            "items": {
                "search": _single_optional_str_search(1)
            }
        },
        "symbol": {
            "search": _single_optional_str_search(2)
        }
    },
})

# TODO: Search? Probably not
HTS_FILE_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_HTS_FILE_SCHEMA, {})

# TODO: search??
VARIANT_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_VARIANT_SCHEMA, {
    "properties": {
        "allele": {"search": {}},  # TODO
        "zygosity": ONTOLOGY_SEARCH_SCHEMA,
    }
})

BIOSAMPLE_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_BIOSAMPLE_SCHEMA, {
    "properties": {
        "id": {
            "search": {
                **_single_optional_eq_search(0, queryable="internal"),
                "database": {"field": models.Biosample._meta.pk.column}
            }
        },
        "individual_id": {  # TODO: Does this work?
            "search": _single_optional_eq_search(1, queryable="internal"),
        },
        "description": {
            "search": _multiple_optional_str_search(2),  # TODO: Searchable? may leak
        },
        "sampled_tissue": ONTOLOGY_SEARCH_SCHEMA,
        "phenotypic_features": {
            "items": PHENOTYPIC_FEATURE_SEARCH_SCHEMA,
            "search": {
                "database": {
                    **PHENOTYPIC_FEATURE_SEARCH_SCHEMA["search"]["database"],
                    "relationship": {
                        "type": "ONE_TO_MANY",
                        "parent_foreign_key": models.PhenotypicFeature._meta.get_field("biosample").column,
                        "parent_primary_key": models.Biosample._meta.pk.column  # TODO: Redundant
                    }
                }
            }
        },
        "taxonomy": ONTOLOGY_SEARCH_SCHEMA,
        # TODO: Front end will need to deal with this:
        # TODO: individual_age_at_collection
        "histological_diagnosis": ONTOLOGY_SEARCH_SCHEMA,
        "tumor_progression": ONTOLOGY_SEARCH_SCHEMA,
        "tumor_grade": ONTOLOGY_SEARCH_SCHEMA,  # TODO: Is this a list?
        "diagnostic_markers": {
            "items": ONTOLOGY_SEARCH_SCHEMA,
            "search": {"database": {"type": "array"}}
        },
        "procedure": {
            "properties": {
                "code": ONTOLOGY_SEARCH_SCHEMA,
                "body_site": ONTOLOGY_SEARCH_SCHEMA
            },
            "search": {
                "database": {
                    "primary_key": models.Procedure._meta.pk.column,
                    "relation": models.Procedure._meta.db_table,
                    "relationship": {
                        "type": "MANY_TO_ONE",
                        "foreign_key": models.Biosample._meta.get_field("procedure").column
                    }
                }
            }
        },
        "hts_files": {
            "items": HTS_FILE_SEARCH_SCHEMA  # TODO
        },
        "variants": {
            "items": VARIANT_SEARCH_SCHEMA,  # TODO: search?
        },
        "is_control_sample": {
            "search": _single_optional_eq_search(1),  # TODO: Boolean search
        },
    },
    "search": {
        "database": {
            "primary_key": models.Biosample._meta.pk.column,
            "relation": models.Biosample._meta.db_table,
        }
    }
})

# TODO
DISEASE_ONSET_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_DISEASE_ONSET_SCHEMA, {})

DISEASE_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_DISEASE_SCHEMA, {
    "properties": {
        "term": ONTOLOGY_SEARCH_SCHEMA,
        "onset": DISEASE_ONSET_SEARCH_SCHEMA,
        "disease_stage": {
            "items": ONTOLOGY_SEARCH_SCHEMA,
            "search": {"database": {"type": "array"}}
        },
        "tnm_finding": {
            "items": ONTOLOGY_SEARCH_SCHEMA,
            "search": {"database": {"type": "array"}}
        },
    },
    "search": {
        "database": {
            "primary_key": models.Disease._meta.pk.column,
            "relation": models.Disease._meta.db_table,
        }
    }
})

# noinspection PyProtectedMember
PHENOPACKET_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_SCHEMA, {
    "properties": {
        "id": {
            "search": {"database": {"field": models.Phenopacket._meta.pk.column}}
        },
        "subject": {
            **INDIVIDUAL_SEARCH_SCHEMA,
            "search": {
                **INDIVIDUAL_SEARCH_SCHEMA["search"],
                "database": {
                    **INDIVIDUAL_SEARCH_SCHEMA["search"]["database"],
                    "relationship": {
                        "type": "MANY_TO_ONE",
                        "foreign_key": models.Phenopacket._meta.get_field("subject").column
                    }
                }
            }
        },
        "phenotypic_features": {
            "items": PHENOTYPIC_FEATURE_SEARCH_SCHEMA,
            "search": {
                "database": {
                    **PHENOTYPIC_FEATURE_SEARCH_SCHEMA["search"]["database"],
                    "relationship": {
                        "type": "ONE_TO_MANY",
                        "parent_foreign_key": "phenopacket_id",  # TODO: No hard-code
                        "parent_primary_key": models.Phenopacket._meta.pk.column  # TODO: Redundant?
                    }
                }
            }
        },
        "biosamples": {
            "items": {
                **BIOSAMPLE_SEARCH_SCHEMA,
                "search": {
                    "database": {
                        **BIOSAMPLE_SEARCH_SCHEMA["search"]["database"],
                        "relationship": {
                            "type": "MANY_TO_ONE",
                            "foreign_key": "biosample_id"  # TODO: No hard-code, from M2M
                        }
                    }
                }
            },
            "search": {
                "database": {
                    "relation": models.Phenopacket._meta.get_field("biosamples").remote_field.through._meta.db_table,
                    "relationship": {
                        "type": "ONE_TO_MANY",
                        "parent_foreign_key": "phenopacket_id",  # TODO: No hard-code
                        "parent_primary_key": models.Phenopacket._meta.pk.column  # TODO: Redundant?
                    }
                }
            }
        },
        "genes": {
            "items": GENE_SEARCH_SCHEMA
        },
        "variants": {
            "items": VARIANT_SEARCH_SCHEMA
        },
        "diseases": {  # TODO: Too sensitive for search?
            "items": {
                **DISEASE_SEARCH_SCHEMA,
                "search": {
                    **DISEASE_SEARCH_SCHEMA["search"],
                    "database": {
                        **DISEASE_SEARCH_SCHEMA["search"]["database"],
                        "relationship": {
                            "type": "MANY_TO_ONE",
                            "foreign_key": "disease_id"  # TODO: No hard-code, from M2M
                        }
                    }
                }
            },
            "search": {
                "database": {
                    "relation": models.Phenopacket._meta.get_field("diseases").remote_field.through._meta.db_table,
                    "relationship": {
                        "type": "ONE_TO_MANY",
                        "parent_foreign_key": "phenopacket_id",  # TODO: No hard-code
                        "parent_primary_key": models.Phenopacket._meta.pk.column  # TODO: Redundant?
                    }
                }
            }
        },  # TODO
        "hts_files": {
            "items": HTS_FILE_SEARCH_SCHEMA  # TODO
        },
        "meta_data": META_DATA_SEARCH_SCHEMA
    },
    "search": {
        "database": {
            "relation": models.Phenopacket._meta.db_table,
            "primary_key": models.Phenopacket._meta.pk.column
        }
    }
})
