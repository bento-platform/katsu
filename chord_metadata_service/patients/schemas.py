from chord_metadata_service.restapi.schema_utils import tag_ids_and_describe
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS, AGE_OR_AGE_RANGE, EXTRA_PROPERTIES_SCHEMA

from .descriptions import INDIVIDUAL
from .values import Sex, KaryotypicSex


INDIVIDUAL_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:patients:individual",
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
            "enum": Sex.as_list(),
            "description": "An individual's phenotypic sex.",
        },
        "karyotypic_sex": {
            "type": "string",
            "enum": KaryotypicSex.as_list(),
            "description": "An individual's karyotypic sex.",
        },
        "taxonomy": ONTOLOGY_CLASS,
        "active": {
            "type": "boolean"
        },
        "deceased": {
            "type": "boolean"
        },
        "extra_properties": EXTRA_PROPERTIES_SCHEMA,
    },
    "required": ["id"]
}, INDIVIDUAL)
