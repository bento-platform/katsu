from rest_framework import serializers
from jsonschema import Draft7Validator, FormatChecker
from .schema_ref import SCHEMA_REFS


__all__ = [
    "JsonSchemaValidator",
    "age_or_age_range_validator",
    "ontology_validator",
    "ontology_list_validator",
    "key_value_validator",
    "base_extra_properties_validator",
]

# Migrations shenanigans:
# Passing full schemas to JsonSchemaValidator can cause huge migrations as soon as a couple of schemas change.
# These migrations include JsonSchemaValidator constructors with the full schema as a param.
# To get around this, David B had the idea of using a schema resolving mechanism instead, where we only pass a
# string ref of the schema to the constructor, this is a small POC of the idea.
'''SCHEMA_REFS: dict[str, dict] = {
    "AGE_OR_AGE_RANGE": AGE_OR_AGE_RANGE,
    "ONTOLOGY_CLASS": ONTOLOGY_CLASS,
    "ONTOLOGY_CLASS_LIST": ONTOLOGY_CLASS_LIST,
    "KEY_VALUE_OBJECT": KEY_VALUE_OBJECT,
    "EXTRA_PROPERTIES_SCHEMA": EXTRA_PROPERTIES_SCHEMA,
}'''

class JsonSchemaValidator:
    """ Custom class based validator to validate against Json schema for JSONField """

    def __init__(self, schema=None, schema_ref=None, formats=None, registry=None):
        """
        Validators can be constructed from a full `schema` object, or a `schema_ref` string.
        """
        if (not schema and not schema_ref) or (schema and schema_ref):
            raise ValueError("Must provide a schema OR a schema_ref argument.")

        # Retrieve schema data from dict when schema_ref is passed
        if schema_ref:
            if schema_ref not in SCHEMA_REFS:
                raise ValueError(f"Schema reference value '{schema_ref}' not present in SCHEMA_REFS keys.")
            schema = SCHEMA_REFS[schema_ref]
        self.schema = schema
        self.schema_ref = schema_ref
        self.formats = formats

        self.validator_args = {
            'schema': self.schema,
            'format_checker': FormatChecker(formats=self.formats),
        }
        if registry:
            self.validator_args['registry'] = registry
        self.validator = Draft7Validator(**self.validator_args)

    def __call__(self, value):
        if not self.validator.is_valid(value):
            raise serializers.ValidationError("Not valid JSON schema for this field.")
        return value

    def __eq__(self, other):
        return self.schema == other.schema

    def deconstruct(self):
        if self.schema_ref:
            # deconstruct using schema reference
            return (
                'chord_metadata_service.restapi.validators.JsonSchemaValidator',
                [],
                {
                    "schema_ref": self.schema_ref,
                    "formats": self.formats
                }
            )
        # deconstruct using schema
        return (
            'chord_metadata_service.restapi.validators.JsonSchemaValidator',
            [self.schema],
            {"formats": self.formats}
        )


# New way of constructing JsonSchemaValidators using schema refs
age_or_age_range_validator = JsonSchemaValidator(schema_ref="AGE_OR_AGE_RANGE")
ontology_validator = JsonSchemaValidator(schema_ref="ONTOLOGY_CLASS")
ontology_list_validator = JsonSchemaValidator(schema_ref="ONTOLOGY_CLASS_LIST")
key_value_validator = JsonSchemaValidator(schema_ref="KEY_VALUE_OBJECT")
base_extra_properties_validator = JsonSchemaValidator(schema_ref="EXTRA_PROPERTIES_SCHEMA")

# TODO: remove, left as an example of schema ref replacement
# age_or_age_range_validator = JsonSchemaValidator(AGE_OR_AGE_RANGE)
# ontology_validator = JsonSchemaValidator(ONTOLOGY_CLASS)
# ontology_list_validator = JsonSchemaValidator(ONTOLOGY_CLASS_LIST)
# key_value_validator = JsonSchemaValidator(KEY_VALUE_OBJECT)
# base_extra_properties_validator = JsonSchemaValidator(EXTRA_PROPERTIES_SCHEMA)
