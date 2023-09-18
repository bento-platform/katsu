import jsonschema

from .logger import logger

__all__ = ["schema_validation"]


def schema_validation(obj, schema):
    v = jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker())
    try:
        v.validate(obj)
        logger.info("JSON schema validation passed.")
        return None
    except jsonschema.exceptions.ValidationError:
        errors = [e for e in v.iter_errors(obj)]
        logger.info("JSON schema validation failed.")
        for i, error in enumerate(errors, 1):
            logger.error(f"{i} Validation error in {'.'.join(str(v) for v in error.path)}: {error.message}")
        return errors
