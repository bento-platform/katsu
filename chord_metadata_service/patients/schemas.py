from chord_metadata_service.restapi.schema_utils import DATE_TIME, DRAFT_07, SCHEMA_TYPES, array_of, base_type, \
    enum_of, tag_ids_and_describe, get_schema_app_id, sub_schema_uri
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS, EXTRA_PROPERTIES_SCHEMA, TIME_ELEMENT_SCHEMA
from pathlib import Path
from .descriptions import INDIVIDUAL, VITAL_STATUS
from .values import Sex, KaryotypicSex


base_uri = get_schema_app_id(Path(__file__).parent.name)

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
        "alternate_ids": array_of(base_type(SCHEMA_TYPES.STRING)),
        "date_of_birth": DATE_TIME,
        "time_at_last_encounter": TIME_ELEMENT_SCHEMA,
        "vital_status": VITAL_STATUS_SCHEMA,
        "sex": enum_of(Sex.as_list(), description="An individual's phenotypic sex."),
        "karyotypic_sex": enum_of(KaryotypicSex.as_list(), description="An individual's karyotypic sex."),
        "gender": ONTOLOGY_CLASS,
        "taxonomy": ONTOLOGY_CLASS,
        # extended fields
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
