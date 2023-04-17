from chord_metadata_service.restapi.schema_utils import customize_schema, tag_ids_and_describe, \
    extra_properties_schema_opt
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS, AGE_OR_AGE_RANGE, EXTRA_PROPERTIES_SCHEMA, \
    KEY_VALUE_OBJECT

from .descriptions import INDIVIDUAL
from .values import Sex, KaryotypicSex


COMORBID_CONDITION = customize_schema(
    first_typeof=ONTOLOGY_CLASS,
    second_typeof=ONTOLOGY_CLASS,
    first_property="clinical_status",
    second_property="code",
    schema_id="katsu:comorbid_condition_schema",
    title="Comorbid Condition schema",
    description="Comorbid condition schema."
)


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
        "race": {
            "type": "string"
        },
        "ethnicity": {
            "type": "string"
        },
        "comorbid_condition": COMORBID_CONDITION,
        "ecog_performance_status": ONTOLOGY_CLASS,
        "karnofsky": ONTOLOGY_CLASS,
        "extra_properties": KEY_VALUE_OBJECT,
    },
    "required": ["id"]
}, INDIVIDUAL)
