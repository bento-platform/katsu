

from django.test import SimpleTestCase

from chord_metadata_service.restapi.schema_ref import SchemaRefs
from chord_metadata_service.restapi.schemas import AGE_OR_AGE_RANGE
from chord_metadata_service.restapi.validators import JsonSchemaValidator

SCHEMA = AGE_OR_AGE_RANGE
SCHEMA_REF_ENUM = SchemaRefs.AGE_OR_AGE_RANGE
SCHEMA_REF_STR = "AGE_OR_AGE_RANGE"
DECONSTRUCTED_SCHEMA = (
    'chord_metadata_service.restapi.validators.JsonSchemaValidator',
    [],
    {'schema_ref': 'AGE_OR_AGE_RANGE', 'formats': None}
)


class TestJsonSchemaValidator(SimpleTestCase):
    def test_init_invalid_exclusive_schema_params(self):
        with self.assertRaises(ValueError):
            JsonSchemaValidator(schema=SCHEMA, schema_ref=SCHEMA_REF_ENUM)

    def test_init_invalid_no_schema_params(self):
        with self.assertRaises(ValueError):
            JsonSchemaValidator(schema=None, schema_ref=None)

    def test_init_schema_valid(self):
        validator = JsonSchemaValidator(schema=SCHEMA)
        self.assertEqual(validator.schema, SCHEMA)

    def test_init_schemaref_str_valid(self):
        validator = JsonSchemaValidator(schema_ref=SCHEMA_REF_STR)
        self.assertEqual(validator.schema_name, SCHEMA_REF_STR)
        self.assertEqual(validator.schema, SCHEMA)

    def test_init_schemaref_enum_valid(self):
        validator = JsonSchemaValidator(schema_ref=SCHEMA_REF_ENUM)
        self.assertEqual(validator.schema_name, SCHEMA_REF_ENUM.name)
        self.assertEqual(validator.schema, SCHEMA)

    def test_equal(self):
        validator_enum = JsonSchemaValidator(schema_ref=SCHEMA_REF_ENUM)
        validator_schema = JsonSchemaValidator(schema=SCHEMA)
        self.assertEqual(validator_enum, validator_schema)

    def test_deconstruct_valid(self):
        validator = JsonSchemaValidator(schema_ref=SCHEMA_REF_ENUM)
        deconstruct = validator.deconstruct()
        self.assertEqual(deconstruct, DECONSTRUCTED_SCHEMA)

    def test_deconstruct_invalid(self):
        validator = JsonSchemaValidator(schema=SCHEMA)
        with self.assertRaises(ValueError):
            validator.deconstruct()
