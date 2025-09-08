from django.http import HttpRequest
from django.test import SimpleTestCase
from rest_framework.request import Request as DrfRequest

from ..pydantic_models import DiscoveryQuery


class TestDiscoveryQueryModel(SimpleTestCase):
    def test_queried_filter_fields(self):
        query = DiscoveryQuery(fts=None, filters={})
        self.assertListEqual(query.queried_filter_fields(), [])
        query = DiscoveryQuery(fts=None, filters={"sex": "MALE", "age": "< 10"})
        self.assertListEqual(query.queried_filter_fields(), ["sex", "age"])

    def test_construction_from_request(self):
        dr = HttpRequest()
        dr.GET["_fts"] = "text"
        fts_q = DiscoveryQuery.from_drf_request(DrfRequest(dr))
        self.assertEqual(fts_q.fts, "text")
        self.assertDictEqual(fts_q.filters, {})

        dr = HttpRequest()
        dr.GET["sex"] = "MALE"
        dr.GET["age"] = "< 10"
        filter_q = DiscoveryQuery.from_drf_request(DrfRequest(dr))
        self.assertIsNone(filter_q.fts)
        self.assertDictEqual(filter_q.filters, {"sex": "MALE", "age": "< 10"})
