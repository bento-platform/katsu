import json
from io import BytesIO

from django.http import HttpRequest
from django.test import SimpleTestCase
from rest_framework.parsers import JSONParser
from rest_framework.request import Request as DrfRequest

from ..pydantic_models import DiscoveryQuery


class TestDiscoveryQueryModel(SimpleTestCase):
    def test_queried_filter_fields(self):
        query = DiscoveryQuery(fts=None, filters={})
        self.assertListEqual(query.queried_filter_fields(), [])
        query = DiscoveryQuery(fts=None, filters={"sex": "MALE", "age": "< 10"})
        self.assertListEqual(query.queried_filter_fields(), ["sex", "age"])

    def test_construction_from_get_request(self):
        dr = HttpRequest()
        dr.method = "GET"
        dr.GET["_fts"] = "text"
        fts_q = DiscoveryQuery.from_drf_request(DrfRequest(dr))
        self.assertEqual(fts_q.fts, "text")
        self.assertDictEqual(fts_q.filters, {})

        dr = HttpRequest()
        dr.method = "GET"
        dr.GET["sex"] = "MALE"
        dr.GET["age"] = "< 10"
        filter_q = DiscoveryQuery.from_drf_request(DrfRequest(dr))
        self.assertIsNone(filter_q.fts)
        self.assertDictEqual(filter_q.filters, {"sex": "MALE", "age": "< 10"})

    def test_construction_from_post_request(self):
        dr = HttpRequest()
        dr.method = "POST"
        dr.content_type = "application/json"
        dr._body = json.dumps({"sex": "MALE", "age": "< 10"}).encode("utf-8")
        dr._stream = BytesIO(json.dumps({"sex": "MALE", "age": "< 10"}).encode("utf-8"))
        filter_q = DiscoveryQuery.from_drf_request(DrfRequest(dr, parsers=(JSONParser,)))
        self.assertIsNone(filter_q.fts)
        self.assertDictEqual(filter_q.filters, {"sex": "MALE", "age": "< 10"})

    def test_construction_bad_method_raise(self):
        with self.assertRaises(NotImplementedError):
            dr = HttpRequest()
            dr.GET["_fts"] = "text"
            DiscoveryQuery.from_drf_request(DrfRequest(dr))
            # Not implemented - method is not GET|POST
