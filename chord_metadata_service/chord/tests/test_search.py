from django.test import TestCase
from jsonschema import Draft7Validator

from chord_metadata_service.phenopackets.search_schemas import PHENOPACKET_SEARCH_SCHEMA
from ..views_search import PHENOPACKET_METADATA_SCHEMA


class SchemaTest(TestCase):
    @staticmethod
    def test_phenopacket_schema():
        Draft7Validator.check_schema(PHENOPACKET_SEARCH_SCHEMA)

    @staticmethod
    def test_phenopacket_metadata_schema():
        Draft7Validator.check_schema(PHENOPACKET_METADATA_SCHEMA)
