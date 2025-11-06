from bento_lib.responses import errors
from django.http import HttpRequest
from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.request import Request as DrfRequest

from chord_metadata_service.discovery.responses import csv_or_json_error_response
from chord_metadata_service.discovery.types import AcceptedDiscoveryResponseFormats


class DiscoveryCsvJsonErrorResponseTest(SimpleTestCase):

    def setUp(self):
        dr = HttpRequest()
        dr.method = "GET"

        self.dummy_request = DrfRequest(dr)

        # noinspection PyTypeChecker
        self.accepted_json_csv: AcceptedDiscoveryResponseFormats = frozenset(("json", "csv"))
        # noinspection PyTypeChecker
        self.accepted_json: AcceptedDiscoveryResponseFormats = frozenset(("json",))
        # noinspection PyTypeChecker
        self.accepted_csv: AcceptedDiscoveryResponseFormats = frozenset(("csv",))

        self.maxDiff = None

    def test_csv_or_json_error_response_json(self):
        json_params = [
            (self.accepted_json_csv, []),
            (self.accepted_json, ["extra_message"]),
            (self.accepted_json, ["extra_message", "extra_message_2"]),
        ]

        for params in json_params:
            with self.subTest(params=params):
                res = csv_or_json_error_response(self.dummy_request, errors.not_found_error(*params[1]), params[0])
                self.assertDictEqual(
                    res.data,
                    {
                        "code": status.HTTP_404_NOT_FOUND,
                        "message": "Not Found",
                        "timestamp": res.data["timestamp"],
                        **({"errors": [{"message": p} for p in params[1]]} if params[1] else {}),
                    }
                )

    def test_csv_or_json_error_response_csv(self):
        csv_params = [
            ([], "code,message,timestamp\r\n404,Not Found,%TS%\r\n"),
            (
                ["extra_message"],
                'code,message,timestamp,errors\r\n404,Not Found,%TS%,"[{""message"": ""extra_message""}]"\r\n',
            ),
            (
                ["extra_message", "extra_message_2"],
                (
                    'code,message,timestamp,errors\r\n'
                    '404,Not Found,%TS%,'
                    '"[{""message"": ""extra_message""}, {""message"": ""extra_message_2""}]"\r\n'
                ),
            )
        ]

        for params in csv_params:
            with self.subTest(params=params):
                err = errors.not_found_error(*params[0])
                res = csv_or_json_error_response(self.dummy_request, err, self.accepted_csv)
                self.assertEqual(res.data, params[1].replace("%TS%", err["timestamp"]).encode("utf-8"))
