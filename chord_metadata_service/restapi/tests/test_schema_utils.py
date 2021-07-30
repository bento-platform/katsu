from django.test import TestCase
from ..schema_utils import merge_schema_dictionaries, tag_schema_with_nested_ids


SCHEMA_1 = {
    "$id": "schema1",
    "type": "object",
    "properties": {
        "key1": {
            "type": "array",
            "items": {
                "type": "string",
            }
        },
        "key2": {
            "type": "object",
            "properties": {
                "key1": {
                    "type": "string",
                }
            }
        },
    },
}


class TestSchemaMerge(TestCase):
    def test_merge_1(self):
        self.assertDictEqual(
            merge_schema_dictionaries({"a": 1}, {"b": 2}),
            {"a": 1, "b": 2})

    def test_merge_2(self):
        self.assertDictEqual(
            merge_schema_dictionaries({"a": 1, "d": 4}, {"a": 2, "b": {"c": 3}}),
            {"a": 2, "d": 4, "b": {"c": 3}})

    def test_merge_3(self):
        self.assertDictEqual(
            merge_schema_dictionaries(
                {"a": {"b": 1}, "c": {"d": {"e": 1}, "f": 5}},
                {"c": {"d": {"g": 8}}}),
            {"a": {"b": 1}, "c": {"d": {"e": 1, "g": 8}, "f": 5}})

    def test_id_tag(self):
        tagged = tag_schema_with_nested_ids(SCHEMA_1)

        self.assertEqual(tagged["properties"]["key1"]["$id"], "schema1:key1")
        self.assertEqual(tagged["properties"]["key1"]["items"]["$id"], "schema1:key1:item")
        self.assertEqual(tagged["properties"]["key2"]["$id"], "schema1:key2")
        self.assertEqual(tagged["properties"]["key2"]["properties"]["key1"]["$id"], "schema1:key2:key1")

    def test_id_raises(self):
        with self.assertRaises(ValueError):
            tag_schema_with_nested_ids({"type": "object", "properties": {"a": {"type": "string"}}})
