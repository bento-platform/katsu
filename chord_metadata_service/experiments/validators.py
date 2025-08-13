from chord_metadata_service.restapi.schema_ref import SchemaRefs
from chord_metadata_service.restapi.validators import JsonSchemaValidator

__all__ = ["file_index_list_validator"]

file_index_list_validator = JsonSchemaValidator(schema_ref=SchemaRefs.EXPERIMENT_RESULT_FILE_INDEX_LIST_SCHEMA)
