from chord_metadata_service.restapi.validators import JsonSchemaValidator
from .schemas import EXPERIMENT_RESULT_FILE_INDEX_LIST_SCHEMA

__all__ = ["file_index_list_validator"]

file_index_list_validator = JsonSchemaValidator(EXPERIMENT_RESULT_FILE_INDEX_LIST_SCHEMA)
