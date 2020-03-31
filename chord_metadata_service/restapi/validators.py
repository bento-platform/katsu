from rest_framework import serializers
from jsonschema import Draft7Validator, FormatChecker
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS, ONTOLOGY_CLASS_LIST, KEY_VALUE_OBJECT, AGE_OR_AGE_RANGE


class JsonSchemaValidator(object):
    """ Custom class based validator to validate against Json schema for JSONField """

    def __init__(self, schema, format_checker=None):
        self.schema = schema
        self.format_checker = format_checker
        self.validator = Draft7Validator(self.schema, format_checker=FormatChecker(formats=self.format_checker))

    def __call__(self, value):
        if not self.validator.is_valid(value):
            raise serializers.ValidationError("Not valid JSON schema for this field.")
        return value

    def __eq__(self, other):
        return self.schema == other.schema

    def deconstruct(self):
        return (
            'chord_metadata_service.restapi.validators.JsonSchemaValidator',
            [self.schema],
            {}
        )


ontologyValidator = JsonSchemaValidator(ONTOLOGY_CLASS)
ontologyListValidator = JsonSchemaValidator(ONTOLOGY_CLASS_LIST)
keyValueValidator = JsonSchemaValidator(KEY_VALUE_OBJECT)
ageOrAgeRangeValidator = JsonSchemaValidator(AGE_OR_AGE_RANGE)
