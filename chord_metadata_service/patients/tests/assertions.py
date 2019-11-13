from jsonschema import validate, ValidationError, Draft7Validator


def assert_valid_schema(data, schema):
	""" Check json data against jsonschema. """
	validation = Draft7Validator(schema).is_valid(data)
	if not validation:
		raise ValidationError("Not valid JSON schema for this field.")
	return data
