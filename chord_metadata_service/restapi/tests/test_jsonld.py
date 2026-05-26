from django.test import SimpleTestCase

from chord_metadata_service.restapi import jsonld_utils as jlu


class JsonLdUtilsTest(SimpleTestCase):
    def test_dataset_to_jsonld_empty_dataset(self):
        result = jlu.dataset_to_jsonld({})
        self.assertIn("@context", result)
        self.assertEqual(result["@type"], "Dataset")

    def test_dataset_to_jsonld_full(self):
        dataset = {
            "dates": [{"type": {}}],
            "stored_in": {},
            "creators": [{"name": "Org"}, {}],
            "types": [{"information": {}}, {}],
            "licenses": [{}],
            "extra_properties": [{"values": [{}]}, {"values": []}],
            "alternate_identifiers": [{}],
            "related_identifiers": [{}],
            "spatial_coverage": [{
                "identifier": {},
                "alternate_identifiers": [{}],
                "related_identifiers": [{}],
            }],
            "distributions": [
                {"stored_in": {}, "dates": [{"type": {}}], "licenses": [{}]},
                {},
            ],
            "dimensions": [{}],
            "primary_publications": [
                {"identifier": {}, "authors": [{"name": "Author"}, {}], "dates": [{"type": {}}]},
                {},
            ],
        }
        result = jlu.dataset_to_jsonld(dataset)
        self.assertIn("@context", result)
        self.assertEqual(result["@type"], "Dataset")
