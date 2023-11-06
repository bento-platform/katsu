from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError

from .logger import logger

__all__ = ["schema_validation"]


def schema_validation(obj, schema, registry=None):
    validator_args = {
        'schema': schema,
        'format_checker': Draft7Validator.FORMAT_CHECKER,
    }

    if registry:
        validator_args['registry'] = registry

    validator = Draft7Validator(**validator_args)
    try:
        validator.validate(obj, schema)
        logger.info("JSON schema validation passed.")
        return True
    except ValidationError:
        errors = [e for e in validator.iter_errors(obj)]
        logger.info("JSON schema validation failed.")
        for i, error in enumerate(errors, 1):
            logger.error(f"{i} Validation error in {'.'.join(str(v) for v in error.path)}: {error.message}")
        return False
