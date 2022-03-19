from . import models, schemas
from chord_metadata_service.restapi.schema_utils import (
    search_optional_eq,
    search_optional_str,
    tag_schema_with_search_properties,
    merge_schema_dictionaries
)
from chord_metadata_service.restapi.search_schemas import ONTOLOGY_SEARCH_SCHEMA

__all__ = ["EXPERIMENT_SEARCH_SCHEMA"]

EXPERIMENT_RESULT_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.EXPERIMENT_RESULT_SCHEMA, {
    "properties": {
        "identifier": {
            "search": search_optional_eq(0)
        },
        "description": {
            "search": search_optional_str(1)
        },
        "filename": {
            "search": search_optional_str(2)
        },
        "file_format": {
            "search": search_optional_eq(3)
        },
        "data_output_type": {
            "search": search_optional_eq(4)
        },
        "usage": {
            "search": search_optional_str(5)
        },
        "genome_assembly_id": {
            "search": search_optional_eq(6)
        },
    },
    "search": {
        "database": {
            "primary_key": models.ExperimentResult._meta.pk.column,
            "relation": models.ExperimentResult._meta.db_table,
        }
    }
})

INSTRUMENT_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.INSTRUMENT_SCHEMA, {
    "properties": {
        "identifier": {
            "search": search_optional_eq(0)
        },
        "platform": {
            "search": search_optional_str(1)
        },
        "description": {
            "search": search_optional_str(2)
        },
        "model": {
            "search": search_optional_str(3)
        },
    },
    "search": {
        "database": {
            "primary_key": models.Instrument._meta.pk.column,
            "relation": models.Instrument._meta.db_table,
        }
    }
})

EXPERIMENT_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.EXPERIMENT_SCHEMA, {
    "properties": {
        "id": {
            "search": {"order": 0, "database": {"field": models.Experiment._meta.pk.column}}
        },
        "reference_registry_id": {
            "search": search_optional_str(1, queryable="internal"),
        },
        "qc_flags": {
            "items": {
                "search": search_optional_str(0),
            },
            "search": {"order": 2, "database": {"type": "array"}}
        },
        "experiment_type": {
            "search": search_optional_str(3),
        },
        "experiment_ontology": {
            "items": ONTOLOGY_SEARCH_SCHEMA,  # TODO: Specific ontology?
            "search": {"order": 4, "database": {"type": "jsonb"}}
        },
        "molecule": {
            "search": search_optional_str(5),
        },
        "molecule_ontology": {
            "items": ONTOLOGY_SEARCH_SCHEMA,  # TODO: Specific ontology?
            "search": {"order": 6, "database": {"type": "jsonb"}}
        },
        "library_strategy": {
            "search": search_optional_str(7),
        },
        "biosample": {
            "search": merge_schema_dictionaries(
                search_optional_eq(8),
                {"database": {"field": models.Experiment._meta.get_field("biosample").column}}
            )
        },
        "extraction_protocol": {
            "search": search_optional_str(9),
        },
        "study_type": {
            "search": search_optional_str(10),
        },
        "library_source": {
            "search": search_optional_str(11),
        },
        "library_selection": {
            "search": search_optional_str(12),
        },
        "library_layout": {
            "search": search_optional_str(13),
        },
        # query example: ["#ico", ["#resolve", "instrument", "model"], "Illumina"]
        "instrument": merge_schema_dictionaries(
            INSTRUMENT_SEARCH_SCHEMA,
            {"search": {"database": {
                "relationship": {
                    "type": "MANY_TO_ONE",
                    "foreign_key": models.Experiment._meta.get_field("instrument").column
                }
            }}}),
        # query example: ["#ico", ["#resolve", "experiment_results", "[item]", "description"], "VCF file"]
        "experiment_results": {
            "items": merge_schema_dictionaries(
                EXPERIMENT_RESULT_SEARCH_SCHEMA,
                {"search": {"database": {
                    "relationship": {
                        "type": "MANY_TO_ONE",
                        "foreign_key": "experimentresult_id"  # TODO: No hard-code, from M2M
                    }
                }}}
            ),
            "search": {
                "database": {
                    "relation": models.Experiment._meta.get_field(
                        "experiment_results").remote_field.through._meta.db_table,
                    "relationship": {
                        "type": "ONE_TO_MANY",
                        "parent_foreign_key": "experiment_id",  # TODO: No hard-code
                        "parent_primary_key": models.Experiment._meta.pk.column
                    }
                }
            }
        },
    },
    "search": {
        "database": {
            "relation": models.Experiment._meta.db_table,
            "primary_key": models.Experiment._meta.pk.column,
        }
    }
})
