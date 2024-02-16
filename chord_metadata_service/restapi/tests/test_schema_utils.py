from django.test import SimpleTestCase, TestCase

from ..schema_utils import merge_schema_dictionaries, tag_schema_with_nested_ids, patch_project_schemas
from ..types import ExtensionSchemaDict
from . import constants as c

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

        self.assertEqual(tagged["properties"]["key1"]["$id"], "schema1/key1")
        self.assertEqual(tagged["properties"]["key1"]["items"]["$id"], "schema1/key1/item")
        self.assertEqual(tagged["properties"]["key2"]["$id"], "schema1/key2")
        self.assertEqual(tagged["properties"]["key2"]["properties"]["key1"]["$id"], "schema1/key2/key1")

    def test_id_raises(self):
        with self.assertRaises(ValueError):
            tag_schema_with_nested_ids({"type": "object", "properties": {"a": {"type": "string"}}})


class TestPatchSchema(SimpleTestCase):

    def test_ignored(self):
        # patch_project_schemas simply returns the base_schema if it has no "type" property
        base_schema = {"$schema": "https://json-schema.org/draft/2020-12/schema"}
        ext_schemas: dict[str, ExtensionSchemaDict] = {
            "phenopacket": {
                "json_schema": {
                    "type": "object"
                },
                "required": False,
                "schema_type": "phenopacket",
            }
        }
        patched = patch_project_schemas(base_schema=base_schema, extension_schemas=ext_schemas)
        self.assertDictEqual(patched, base_schema)

    def test_patched_object(self):
        base_schema = c.VALID_PHENOPACKET_SCHEMA
        ext_schemas = c.VALID_EXTRA_PROPERTIES_EXTENSIONS
        base_schema = tag_schema_with_nested_ids(base_schema)
        patched_schema = patch_project_schemas(base_schema=base_schema, extension_schemas=ext_schemas)
        self.assertDictEqual(
            patched_schema["properties"]["phenopacket"]["properties"]["extra_properties"],
            ext_schemas["phenopacket"]["json_schema"]
        )
        self.assertDictEqual(
            (patched_schema["properties"]["phenopacket"]["properties"]["biosamples"]["items"]
                ["properties"]["extra_properties"]),
            ext_schemas["biosample"]["json_schema"]
        )
