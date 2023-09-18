from typing import List
from jsonschema.exceptions import ValidationError

__all__ = [
    "IngestError",
]


def parse_validation_errors(errors: List[ValidationError]):
    error_descriptions = {}
    for error in errors:
        field_path = ".".join(error.schema_path)
        error_descriptions[field_path] = {
            "faulty_value": error.instance,
            "valid_options": error.validator_value,
            "field_schema": error.schema,
            "message": error.message,
        }
    return error_descriptions


class IngestError(Exception):

    def __init__(self, schema_validation_errors=[], message="An error occured during ingestion."):

        errors_descriptions = parse_validation_errors(schema_validation_errors)

        self.validation_errors = errors_descriptions
        self.message = message
