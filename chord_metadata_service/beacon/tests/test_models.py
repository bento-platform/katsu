import json

from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import RequestFactory, SimpleTestCase
from pydantic import ValidationError
from rest_framework.parsers import JSONParser
from rest_framework.request import Request as DrfRequest

from chord_metadata_service.authz.types import DataPermissions

from ..models import (
    BeaconAlphanumericFilter,
    BeaconBooleanResponse,
    BeaconCountResponse,
    BeaconCustomFilter,
    BeaconRequest,
    BeaconResultsetsResponse,
)


class BeaconRequestModelTest(SimpleTestCase):
    def test_from_post_request_validates_beacon_body(self):
        request = RequestFactory().post(
            "/beacon/g_variants",
            data=json.dumps({"meta": {"apiVersion": "v2.0.0"}, "query": {"requestedGranularity": "count"}}),
            content_type="application/json",
        )
        drf_request = DrfRequest(request, parsers=(JSONParser(),))

        beacon_request = BeaconRequest.from_drf_request(drf_request)

        self.assertEqual(beacon_request.meta.api_version, "v2.0.0")
        self.assertEqual(beacon_request.query.requested_granularity, "count")

    def test_from_get_request_builds_beacon_query(self):
        request = RequestFactory().get(
            "/beacon/g_variants",
            {
                "referenceName": "1",
                "start": ["10", "20"],
                "requestedGranularity": "count",
                "filters": json.dumps({"id": "HP:0001250", "includeDescendantTerms": False}),
                "skip": "5",
                "limit": "15",
            },
        )

        beacon_request = BeaconRequest.from_drf_request(DrfRequest(request))

        self.assertEqual(beacon_request.meta.api_version, "v2.2.0")
        self.assertEqual(beacon_request.query.requested_granularity, "count")
        self.assertEqual(beacon_request.query.request_parameters.g_variant.reference_name, "1")
        self.assertEqual(beacon_request.query.request_parameters.g_variant.start, [10, 20])
        self.assertEqual(beacon_request.query.filters[0].id, "HP:0001250")
        self.assertEqual(beacon_request.query.pagination.skip, 5)
        self.assertEqual(beacon_request.query.pagination.limit, 15)

    def test_permissions_match_requested_granularity(self):
        request = BeaconRequest(
            meta={"apiVersion": "v2.0.0"},
            query={"requestedGranularity": "count"},
        )

        request.get_and_validate_permissions(DataPermissions(bool_=True, counts=True, data=False))

        with self.assertRaises(DjangoValidationError):
            request.get_and_validate_permissions(DataPermissions(bool_=True, counts=False, data=False))

    def test_request_body_uses_beacon_field_names(self):
        request = BeaconRequest.model_validate(
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "meta": {
                    "apiVersion": "v2.0.0",
                    "requestedSchemas": [{"entityType": "individual", "schema": "example"}],
                },
                "query": {
                    "requestParameters": {"g_variant": {"referenceName": "1", "start": [10]}},
                    "filters": [{"id": "HP:0001250", "includeDescendantTerms": False}],
                    "includeResultsetResponses": "HIT",
                    "pagination": {"skip": 2, "limit": 25},
                    "requestedGranularity": "count",
                    "testMode": True,
                },
            }
        )

        self.assertEqual(request.meta.api_version, "v2.0.0")
        self.assertEqual(request.query.requested_granularity, "count")
        self.assertEqual(request.model_dump(by_alias=True)["query"]["testMode"], True)
        self.assertEqual(request.query.request_parameters.g_variant.start, [10])
        self.assertEqual(
            request.model_dump(by_alias=True)["query"]["requestParameters"]["g_variant"]["referenceName"], "1"
        )

    def test_defaults_match_beacon_schema(self):
        request = BeaconRequest(meta={"apiVersion": "v2.0.0"})

        self.assertEqual(request.query, None)
        self.assertEqual(BeaconRequest.model_json_schema()["required"], ["meta"])

    def test_genomic_variant_request_parameters_validate_schema_constraints(self):
        for parameters in ({"start": [-1]}, {"referenceBases": "ACGX"}):
            with self.subTest(parameters=parameters), self.assertRaises(ValidationError):
                BeaconRequest(
                    meta={"apiVersion": "v2.0.0"},
                    query={"requestParameters": {"g_variant": parameters}},
                )

    def test_filter_variants(self):
        query = BeaconRequest(
            meta={"apiVersion": "v2.0.0"},
            query={
                "filters": [
                    {"id": "age", "operator": ">", "value": "18"},
                    {"id": "custom", "scope": "individuals", "value": "x"},
                ]
            },
        ).query

        self.assertIsInstance(query.filters[0], BeaconAlphanumericFilter)
        self.assertIsInstance(query.filters[1], BeaconCustomFilter)

    def test_api_version_and_pagination_are_required_or_nonnegative(self):
        with self.assertRaises(ValidationError):
            BeaconRequest(meta={})
        with self.assertRaises(ValidationError):
            BeaconRequest(meta={"apiVersion": "v2.0.0"}, query={"pagination": {"skip": -1}})


class BeaconResponseModelTest(SimpleTestCase):
    def response_meta(self):
        return {
            "beaconId": "example-beacon",
            "apiVersion": "v2.0.0",
            "returnedSchemas": [],
            "returnedGranularity": "record",
            "receivedRequestSummary": {
                "apiVersion": "v2.0.0",
                "requestedSchemas": [],
                "pagination": {"skip": 0, "limit": 10},
                "requestedGranularity": "record",
            },
        }

    def test_resultsets_response_uses_response_result_sets(self):
        response = BeaconResultsetsResponse(
            meta=self.response_meta(),
            responseSummary={"exists": True, "numTotalResults": 1},
            response={
                "resultSets": [
                    {
                        "id": "datasetA",
                        "setType": "dataset",
                        "exists": True,
                        "resultsCount": 1,
                        "results": [{"id": "record-1"}],
                    }
                ]
            },
        )

        self.assertEqual(response.response.result_sets[0].set_type, "dataset")
        self.assertEqual(response.model_dump(by_alias=True)["response"]["resultSets"][0]["results"], [{"id": "record-1"}])

    def test_boolean_and_count_response_summaries(self):
        boolean = BeaconBooleanResponse(meta=self.response_meta(), responseSummary={"exists": False})
        count = BeaconCountResponse(meta=self.response_meta(), responseSummary={"exists": True, "numTotalResults": 2})

        self.assertFalse(boolean.response_summary.exists)
        self.assertEqual(count.response_summary.num_total_results, 2)

    def test_resultset_requires_schema_fields(self):
        with self.assertRaises(ValidationError):
            BeaconResultsetsResponse(
                meta=self.response_meta(),
                responseSummary={"exists": False},
                response={"resultSets": [{"id": "datasetA", "exists": False}]},
            )
