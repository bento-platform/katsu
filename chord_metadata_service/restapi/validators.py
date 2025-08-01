from rest_framework import serializers
from jsonschema import Draft7Validator, FormatChecker
from .schema_ref import SchemaRefs


__all__ = [
    "JsonSchemaValidator",
    "age_or_age_range_validator",
    "ontology_validator",
    "ontology_list_validator",
    "key_value_validator",
    "base_extra_properties_validator",
]


class JsonSchemaValidator:
    """ Custom class based validator to validate against Json schema for JSONField """

    def __init__(self, schema=None, schema_ref: SchemaRefs | str = None, formats=None, registry=None):
        """
        Validators should be constructed from a `SchemaRefs` enum value.
        However, for migration purposes, construction from either full `schema` or a `schema_ref` string is possible.
        """
        if (not schema and not schema_ref) or (schema and schema_ref):
            raise ValueError("Must provide a schema OR a schema_ref argument.")

        if schema_ref:
            schema_ref = SchemaRefs[schema_ref] if isinstance(schema_ref, str) else schema_ref
            self.schema_name = schema_ref.name
            schema = schema_ref.value

        self.schema = schema
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
        if self.schema_name:
            # deconstruct using schema reference
            return (
                'chord_metadata_service.restapi.validators.JsonSchemaValidator',
                [],
                {
                    "schema_ref": self.schema_name,
                    "formats": self.formats
                }
            )
        # deconstruct using schema
        raise ValueError("JsonSchemaValidator has no schema_ref."
                         + "Please construct your validator using schema_ref, NOT via JSON schema!")


age_or_age_range_validator = JsonSchemaValidator(schema_ref=SchemaRefs.AGE_OR_AGE_RANGE)
ontology_validator = JsonSchemaValidator(schema_ref=SchemaRefs.ONTOLOGY_CLASS)
ontology_list_validator = JsonSchemaValidator(schema_ref=SchemaRefs.ONTOLOGY_CLASS_LIST)
key_value_validator = JsonSchemaValidator(schema_ref=SchemaRefs.KEY_VALUE_OBJECT)
base_extra_properties_validator = JsonSchemaValidator(schema_ref=SchemaRefs.EXTRA_PROPERTIES_SCHEMA)
