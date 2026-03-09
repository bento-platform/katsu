import json
from io import BytesIO

from django.http import HttpRequest
from django.test import SimpleTestCase
from rest_framework.parsers import JSONParser
from rest_framework.request import Request as DrfRequest

from ..pydantic_models import DiscoveryQuery


class TestDiscoveryQueryModel(SimpleTestCase):
    def test_empty_queries(self):
        query = DiscoveryQuery()
        self.assertListEqual(query.queried_filter_fields(), [])
        self.assertTrue(query.is_empty())

        query = DiscoveryQuery(filters={})
        self.assertListEqual(query.queried_filter_fields(), [])
        self.assertTrue(query.is_empty())

        query = DiscoveryQuery(fts="", filters={})
        self.assertListEqual(query.queried_filter_fields(), [])
        self.assertTrue(query.is_empty())

    def test_queried_filter_fields(self):
        query = DiscoveryQuery(filters={"sex": "MALE", "age": "< 10"})
        self.assertListEqual(query.queried_filter_fields(), ["sex", "age"])
        self.assertFalse(query.is_empty())

    def test_construction_from_get_request(self):
        dr = HttpRequest()
        dr.method = "GET"
        dr.GET["_fts"] = "text"
        fts_q = DiscoveryQuery.from_drf_request(DrfRequest(dr))
        self.assertEqual(fts_q.fts, "text")
        self.assertEqual(fts_q.fts_type, "plain")  # default
        self.assertDictEqual(fts_q.filters, {})

        dr = HttpRequest()
        dr.method = "GET"
        dr.GET["_fts"] = "'text' | 'text2'"
        dr.GET["_fts_type"] = "websearch"
        fts_q = DiscoveryQuery.from_drf_request(DrfRequest(dr))
        self.assertEqual(fts_q.fts, "'text' | 'text2'")
        self.assertEqual(fts_q.fts_type, "websearch")
        self.assertDictEqual(fts_q.filters, {})
        self.assertFalse(fts_q.is_empty())

        dr = HttpRequest()
        dr.method = "GET"
        dr.GET["sex"] = "MALE"
        dr.GET["age"] = "< 10"
        filter_q = DiscoveryQuery.from_drf_request(DrfRequest(dr))
        self.assertEqual(filter_q.fts, "")  # no FTS
        self.assertDictEqual(filter_q.filters, {"sex": "MALE", "age": "< 10"})
        self.assertFalse(filter_q.is_empty())

    @staticmethod
    def _mock_json_post(content: dict | list):
        dr = HttpRequest()
        dr.content_type = "application/json"
        dr.method = "POST"
        dr.META["CONTENT_TYPE"] = "application/json"

        r = DrfRequest(dr, parsers=(JSONParser(),))
        r._stream = BytesIO(json.dumps(content).encode("utf-8"))
        r._load_data_and_files()

        return r

    def test_construction_from_post_request(self):
        filter_q = DiscoveryQuery.from_drf_request(self._mock_json_post({"sex": "MALE", "age": "< 10"}))
        self.assertEqual(filter_q.fts, "")  # no FTS
        self.assertEqual(filter_q.fts_type, "plain")  # default
        self.assertDictEqual(filter_q.filters, {"sex": "MALE", "age": "< 10"})

        fts_params = [
            ({"_fts": "abc"}, "abc", "plain"),
            ({"_fts": "abc", "_fts_type": "phrase"}, "abc", "phrase"),
            ({"_fts": "'a' | 'b'", "_fts_type": "websearch"}, "'a' | 'b'", "websearch"),
        ]

        for params in fts_params:
            with self.subTest(params=params):
                q = DiscoveryQuery.from_drf_request(self._mock_json_post(params[0]))
                self.assertEqual(q.fts, params[1])
                self.assertEqual(q.fts_type, params[2])  # default: plain
                self.assertDictEqual(q.filters, {})

    def test_construction_bad_method_raise(self):
        with self.assertRaises(NotImplementedError):
            dr = HttpRequest()
            dr.GET["_fts"] = "text"
            DiscoveryQuery.from_drf_request(DrfRequest(dr))
            # Not implemented - method is not GET|POST

    def test_construction_blank_fts_from_request(self):
        q = DiscoveryQuery.from_drf_request(self._mock_json_post({}))
        self.assertEqual(q.fts, "")
