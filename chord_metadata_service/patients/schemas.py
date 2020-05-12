from chord_metadata_service.restapi.schema_utils import customize_schema
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS


COMORBID_CONDITION = customize_schema(
    first_typeof=ONTOLOGY_CLASS,
    second_typeof=ONTOLOGY_CLASS,
    first_property="clinical_status",
    second_property="code",
    schema_id="chord_metadata_service:comorbid_condition_schema",
    title="Comorbid Condition schema",
    description="Comorbid condition schema."
)
