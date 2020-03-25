from rest_framework import serializers
from jsonschema import Draft7Validator

class JsonSchemaValidator(object):
    """ Custom class based validator to validate against Json schema for JSONField """

    def __init__(self, schema):
        self.schema = schema
        self.validator = Draft7Validator(self.schema)

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
