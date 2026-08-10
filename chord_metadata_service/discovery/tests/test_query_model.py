import json
import sys
from io import BytesIO

from django.http import HttpRequest
from django.test import SimpleTestCase
from pydantic import ValidationError
from rest_framework.parsers import JSONParser
from rest_framework.request import Request as DrfRequest

from ..pydantic_models import DiscoveryQuery, DiscoveryQueryFilterOneOf


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
        self.assertEqual(fts_q.n_filter_parameters(), 0)

        dr = HttpRequest()
        dr.method = "GET"
        dr.GET["_fts"] = "'text' | 'text2'"
        dr.GET["_fts_type"] = "websearch"
        fts_q = DiscoveryQuery.from_drf_request(DrfRequest(dr))
        self.assertEqual(fts_q.fts, "'text' | 'text2'")
        self.assertEqual(fts_q.fts_type, "websearch")
        self.assertDictEqual(fts_q.filters, {})
        self.assertFalse(fts_q.is_empty())
        self.assertEqual(fts_q.n_filter_parameters(), 0)

        dr = HttpRequest()
        dr.method = "GET"
        dr.GET["sex"] = "MALE"
        dr.GET["age"] = "< 10"
        filter_q = DiscoveryQuery.from_drf_request(DrfRequest(dr))
        self.assertEqual(filter_q.fts, "")  # no FTS
        self.assertDictEqual(filter_q.filters, {"sex": "MALE", "age": "< 10"})
        self.assertFalse(filter_q.is_empty())
        self.assertEqual(filter_q.n_filter_parameters(), 2)

        dr = HttpRequest()
        dr.method = "GET"
        dr.GET.setlist("age", [])
        filter_q = DiscoveryQuery.from_drf_request(DrfRequest(dr))
        self.assertEqual(filter_q.fts, "")  # no FTS
        self.assertDictEqual(filter_q.filters, {})  # empty array shouldn't be picked up
        self.assertTrue(filter_q.is_empty())
        self.assertEqual(filter_q.n_filter_parameters(), 0)

    @staticmethod
    def _mock_json_post(content: dict | list):
        dr = HttpRequest()
        dr._read_started = False
        dr.content_type = "application/json"
        dr.method = "POST"
        dr.META["CONTENT_TYPE"] = "application/json"

        r = DrfRequest(dr, parsers=(JSONParser(),))
        r._stream = BytesIO(json.dumps(content).encode("utf-8"))
        r._load_data_and_files()

        return r

    def test_construction_from_post_request(self):
        filter_params = [
            ({"sex": "MALE", "age": "< 10"}, {"sex": "MALE", "age": "< 10"}, 2),
            (
                {"sex": "MALE", "age": ["< 10", "[20, 30)"]},
                {"sex": "MALE", "age": DiscoveryQueryFilterOneOf(filter_type="one_of", values=["< 10", "[20, 30)"])},
                sys.maxsize - 2,  # subtracted len(filters) to avoid going over an "infinite" cap on # filters
            ),
            (
                {"sex": "MALE", "age": {"filter_type": "one_of", "values": ["< 10", "[20, 30)"]}},
                {"sex": "MALE", "age": DiscoveryQueryFilterOneOf(filter_type="one_of", values=["< 10", "[20, 30)"])},
                sys.maxsize - 2,  # subtracted len(filters) to avoid going over an "infinite" cap on # filters
            ),
        ]

        for params in filter_params:
            with self.subTest(params=params):
                filter_q = DiscoveryQuery.from_drf_request(self._mock_json_post(params[0]))
                self.assertEqual(filter_q.fts, "")  # no FTS
                self.assertEqual(filter_q.fts_type, "plain")  # default
                self.assertDictEqual(filter_q.filters, params[1])
                self.assertEqual(filter_q.n_filter_parameters(), params[2])

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

    def test_construction_from_bad_post_request(self):
        with self.assertRaises(ValidationError):
            DiscoveryQuery.from_drf_request(
                # should be values not vals
                self._mock_json_post({"sex": "MALE", "age": {"filter_type": "one_of", "vals": ["< 10", "[20, 30)"]}})
            )

    def test_construction_bad_method_raise(self):
        with self.assertRaises(NotImplementedError):
            dr = HttpRequest()
            dr.GET["_fts"] = "text"
            DiscoveryQuery.from_drf_request(DrfRequest(dr))
            # Not implemented - method is not GET|POST

    def test_construction_blank_fts_from_request(self):
        q = DiscoveryQuery.from_drf_request(self._mock_json_post({}))
        self.assertEqual(q.fts, "")
