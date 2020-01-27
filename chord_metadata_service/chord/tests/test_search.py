from django.test import TestCase
from jsonschema import Draft7Validator

from ..views_search import PHENOPACKET_SCHEMA, PHENOPACKET_METADATA_SCHEMA


class SchemaTest(TestCase):
    @staticmethod
    def test_phenopacket_schema():
        Draft7Validator.check_schema(PHENOPACKET_SCHEMA)

    @staticmethod
    def test_phenopacket_metadata_schema():
        Draft7Validator.check_schema(PHENOPACKET_METADATA_SCHEMA)
