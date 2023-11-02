from chord_metadata_service.restapi.schema_utils import DATE_TIME, DRAFT_07, SCHEMA_TYPES, array_of, base_type, \
    customize_schema, enum_of, tag_ids_and_describe, get_schema_app_id, sub_schema_uri
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS, EXTRA_PROPERTIES_SCHEMA, TIME_ELEMENT_SCHEMA, \
    CURIE_SCHEMA
from pathlib import Path
from .descriptions import INDIVIDUAL, VITAL_STATUS
from .values import Sex, KaryotypicSex


base_uri = get_schema_app_id(Path(__file__).parent.name)

COMORBID_CONDITION = customize_schema(
    first_typeof=ONTOLOGY_CLASS,
    second_typeof=ONTOLOGY_CLASS,
    first_property="clinical_status",
    second_property="code",
    schema_id=sub_schema_uri(base_uri, "comorbid_condition_schema"),
    title="Comorbid Condition schema",
    description="Comorbid condition schema."
)

VITAL_STATUS_SCHEMA = tag_ids_and_describe({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "vital_status"),
    "type": "object",
    "properties": {
        "status": enum_of(["UNKNOWN_STATUS", "ALIVE", "DECEASED"]),
        "time_of_death": TIME_ELEMENT_SCHEMA,
        "cause_of_death": ONTOLOGY_CLASS,
        "survival_time_in_days": base_type(SCHEMA_TYPES.INTEGER)
    },
    "required": ["status"]
}, VITAL_STATUS)

INDIVIDUAL_SCHEMA = tag_ids_and_describe({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "individual"),
    "type": "object",
    "properties": {
        # Phenopacket V2 Individual fields
        "id": base_type(SCHEMA_TYPES.STRING, description="Unique researcher-specified identifier for the individual."),
        "alternate_ids": array_of(CURIE_SCHEMA, description="A list of alternative identifiers for the individual."),
        "date_of_birth": DATE_TIME,
        "time_at_last_encounter": TIME_ELEMENT_SCHEMA,
        "vital_status": VITAL_STATUS_SCHEMA,
        "sex": enum_of(Sex.as_list(), description="An individual's phenotypic sex."),
        "karyotypic_sex": enum_of(KaryotypicSex.as_list(), description="An individual's karyotypic sex."),
        "gender": ONTOLOGY_CLASS,
        "taxonomy": ONTOLOGY_CLASS,

        # Extended schema fields
        "active": base_type(SCHEMA_TYPES.BOOLEAN),
        "deceased": base_type(SCHEMA_TYPES.BOOLEAN),
        "race": base_type(SCHEMA_TYPES.STRING),
        "ethnicity": base_type(SCHEMA_TYPES.STRING),
        "comorbid_condition": COMORBID_CONDITION,
        "ecog_performance_status": ONTOLOGY_CLASS,
        "karnofsky": ONTOLOGY_CLASS,
        "extra_properties": EXTRA_PROPERTIES_SCHEMA,
    },
    "required": ["id"]
}, INDIVIDUAL)
