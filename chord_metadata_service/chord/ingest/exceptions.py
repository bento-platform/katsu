from typing import List, Optional
from jsonschema.exceptions import ValidationError
from chord_metadata_service import __version__
from chord_metadata_service.experiments.schemas import EXPERIMENT_SCHEMA_CHANGES
from chord_metadata_service.chord.data_types import DATA_TYPE_EXPERIMENT, DATA_TYPE_PHENOPACKET

__all__ = [
    "IngestError",
]


DATA_TYPE_SCHEMA_CHANGES = {
    DATA_TYPE_EXPERIMENT: EXPERIMENT_SCHEMA_CHANGES,
    DATA_TYPE_PHENOPACKET: None
}


def parse_validation_errors(errors: List[ValidationError]) -> Optional[List[dict]]:
    """
    Accepts a list of jsonschema ValidationError and converts them to a client error format.

    Parameters:
        errors (List[ValidationError]): errors raised by jsonschema during validation
    Returns:
        List[dict]:
            dict:
                schema_path (str): Schema path string (e.g "properties.library_strategy")
                faulty_value (str | obj): The value at the schema_path causing the error
                property_schema (dict): JSON schema of the property (includes valid options)
                message (str): The ValidationError.message
    """
    error_descriptions = []
    for error in errors:
        schema_path = ".".join(error.schema_path)
        error_descriptions.append({
            "schema_path": schema_path,
            "faulty_value": error.instance,
            "message": error.message,
            "property_schema": error.schema,
        })
    return error_descriptions if len(error_descriptions) else None


def parse_property_warnings(data: dict, prop_name: str, property_changes: List[tuple]) -> Optional[dict]:
    for (old_value, new_value) in property_changes:
        value = data[prop_name]
        property_warning = {
                "property_name": prop_name,
                "property_value": value,
                "deprecated_value": old_value,
                "suggested_replacement": new_value,
        }

        if value == old_value:
            # Naive comparison for dicts
            return property_warning

        if isinstance(value, str) and isinstance(old_value, str):
            # Lower case comparison for string values (JSON schema enum)
            if value.lower() == old_value.lower():
                return property_warning

        # Only warn when necessary
        return None


def parse_schema_warnings(data: dict, schema: dict) -> Optional[List[dict]]:
    """
    Schema warnings are issued on Katsu releases that include schema changes.
    Warnings are returned to highlight schema changes that may be the root cause of an IngestionError.

    Parameters:
        data (dict): the data submitted for ingestion

    Returns:
        List[dict]:
            dict:
                property_name (str): The name of the property
                property_value (str | dict)
                deprecated_value (str | dict): The deprecated property option
                suggested_replacement (str | dict): The new suggested property option
                version (str): The Katsu release version associated with the schema change
    """
    if not data or not schema:
        return None

    data_type = schema.get("$id", "").split("/")[-1]
    applicable_changes = DATA_TYPE_SCHEMA_CHANGES.get(data_type, None)

    if not applicable_changes or __version__ not in applicable_changes:
        # Skip if data type's schema is not affected in current Katsu version
        return None

    warnings = []
    for (version, version_changes) in applicable_changes.items():
        for (prop_name, changes) in version_changes.get("properties", {}).items():
            if property_warning := parse_property_warnings(data, prop_name, changes):
                property_warning["version"] = version
                warnings.append(property_warning)
    return warnings if len(warnings) else None


class IngestError(Exception):

    def __init__(self,
                 data: dict = None,
                 schema: dict = None,
                 schema_validation_errors: List[ValidationError] = [],
                 message="An error occured during ingestion."):

        self.validation_errors = parse_validation_errors(schema_validation_errors)
        self.schema_warnings = parse_schema_warnings(data=data, schema=schema)
        self.message = message
