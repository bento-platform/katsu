from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError
from referencing import Registry
from structlog.stdlib import BoundLogger

from chord_metadata_service.logger import logger as logger_

__all__ = ["schema_validation"]


def extract_error_msg(errors: list[ValidationError]) -> str:
    """
    Helper to format the first validation error into a readable string.
    """
    if not errors:
        return "Unknown validation error"
    first_error = errors[0]
    error_path = " -> ".join(map(str, first_error.path)) or "root"
    return f"at field '{error_path}': {first_error.message}"


def schema_validation(
    obj,
    schema,
    registry: Registry = None,
    obj_idx: int | None = None,
    logger: BoundLogger | None = None,
    validation_errors: list | None = None
):
    """
    Validates an object (obj) against a json-schema (schema).
    May use a referencing.Registry object to resolve schema definitions (e.g. VRS variation schemas).
    An object index may be passed for logging/debugging purposes.
    """

    schema_id: str | None = schema.get("$id")

    lg: BoundLogger = logger or logger_
    lg = lg.bind(schema_id=schema_id)

    if obj_idx is not None:
        lg = lg.bind(obj_idx=obj_idx)

    validator_args = {
        'schema': schema,
        'format_checker': Draft7Validator.FORMAT_CHECKER,
    }

    if registry:
        validator_args['registry'] = registry

    validator = Draft7Validator(**validator_args)
    try:
        validator.validate(obj, schema)
        lg.info("JSON schema validation passed")
        return True
    except ValidationError:
        errors = [e for e in validator.iter_errors(obj)]
        if validation_errors is not None:
            validation_errors.extend(errors)

        lg.info(
            "JSON schema validation failed",
            errors=[
                {"idx": i, "path": '.'.join(str(v) for v in error.path), "message": error.message}
                for i, error in enumerate(errors)
            ]
        )
        return False
