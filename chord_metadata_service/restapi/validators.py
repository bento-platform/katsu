from rest_framework import serializers
from jsonschema import Draft7Validator


class JsonSchemaValidator(object):
    """ Custom class based validator to validate against Json schema for JSONField """

    def __init__(self, schema):
        self.schema = schema

    def __call__(self, value):
        validation = Draft7Validator(self.schema).is_valid(value)
        if not validation:
            raise serializers.ValidationError("Not valid JSON schema for this field.")
        return value
