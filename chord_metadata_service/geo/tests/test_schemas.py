from django.test import SimpleTestCase
from jsonschema.validators import Draft7Validator

from ..schemas import GEO_LOCATION_SCHEMA


class ValidSchemasTest(SimpleTestCase):
    @staticmethod
    def test_geo_location_schema():
        Draft7Validator.check_schema(GEO_LOCATION_SCHEMA)
