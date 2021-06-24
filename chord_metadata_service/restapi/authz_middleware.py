from django.conf import settings
from django.http import HttpResponseServerError
import requests
import json
import os
import re

REQUEST_PATHS_TO_AUTHZ_PATHS = {"/api/phenopackets": "api/phenopackets",
                                "/api/individuals": "api/ga4gh/individuals"}

AUTHZ_PATHS = ["^/api/phenopackets/?.*", "^/api/datasets/?.*", "^/api/diagnoses/?.*", "^/api/diseases/?.*",
               "^/api/genes/?.*", "^/api/genomicinterpretations/?.*", "^/api/htsfiles/?.*", "^/api/individuals/?.*",
               "^/api/interpretations/?.*", "^/api/metadata/?.*", "^/api/phenopackets/?.*",
               "^/api/phenotypicfeatures/?.*", "^/api/procedures/?.*", "^/api/variants/?.*"]
rootCA = os.getenv("ROOT_CA", None)
CANDIG_OPA_VERSION = os.getenv("CANDIG_OPA_VERSION", "dycons")
permissions_secret = os.getenv("PERMISSIONS_SECRET",
                               "my-secret-beacon-token")


class AuthzMiddleware:
    """
    Middleware for dataset-level authorization.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # auth for current dycons
        if CANDIG_OPA_VERSION == "dycons" and request.path in REQUEST_PATHS_TO_AUTHZ_PATHS and request.method == "GET":
            tokens = {}
            for header in request.headers:
                header_all_caps = header.upper()
                if header_all_caps.startswith(("X-CANDIG-LOCAL-", "X-CANDIG-DAC-", "X-CANDIG-FED-", "X-CANDIG-EXT-")):
                    tokens[header] = json.loads(request.headers[header])

            request_body = {
                "input": {
                    "headers": tokens,
                    "body": {
                        "path": REQUEST_PATHS_TO_AUTHZ_PATHS[request.path],
                        "method": request.method
                    }
                }
            }
            if settings.CANDIG_OPA_URL:
                try:
                    response = requests.post(settings.CANDIG_OPA_URL +
                                             "/v1/data/ga4ghPassport/tokenControlledAccessREMS",
                                             json=request_body)
                    response.raise_for_status()
                except requests.exceptions.RequestException:
                    error_response = {
                        "error": "error getting response from authorization service"
                    }
                    response = HttpResponseServerError(json.dumps(error_response))
                    response["Content-Type"] = "application/json"
                    return response

                allowed_datasets = response.json()["result"]
                request.allowed_datasets = allowed_datasets
        # auth for rego_dev_playground repo
        elif (CANDIG_OPA_VERSION == "rego_dev_playground" and
              any(re.match(path_re, request.path) for path_re in AUTHZ_PATHS) and
              request.method == "GET"):
            tokens = {}
            for header in request.headers:
                header_all_caps = header.upper()
                if header_all_caps.startswith(("X-CANDIG-LOCAL-", "X-CANDIG-DAC-", "X-CANDIG-FED-", "X-CANDIG-EXT-")):
                    tokens[header] = json.loads(request.headers[header])

            request_body = {
                "input": {
                    "headers": tokens,
                    "body": {
                        "path": request.path,
                        "method": request.method
                    }
                }
            }

            if settings.CANDIG_OPA_URL:
                # get dataset permissions
                try:
                    response = requests.post(settings.CANDIG_OPA_URL +
                                             "/v1/data/permissions/datasets",
                                             headers={"Authorization": f"Bearer {permissions_secret}"},
                                             json=request_body,
                                             verify=rootCA)
                    response.raise_for_status()
                except requests.exceptions.RequestException:
                    error_response = {
                        "error": "error getting response from authorization service"
                    }
                    response = HttpResponseServerError(json.dumps(error_response))
                    response["Content-Type"] = "application/json"
                    return response

                allowed_datasets = response.json()["result"]
                request.allowed_datasets = allowed_datasets

                # get count permissions
                try:
                    request_body["input"]["body"]["query_type"] = "counts"
                    response = requests.post(settings.CANDIG_OPA_URL +
                                             "/v1/data/permissions/datasets",
                                             headers={"Authorization": f"Bearer {permissions_secret}"},
                                             json=request_body,
                                             verify=rootCA)
                    response.raise_for_status()
                except requests.exceptions.RequestException:
                    error_response = {
                        "error": "error getting response from authorization service"
                    }
                    response = HttpResponseServerError(json.dumps(error_response))
                    response["Content-Type"] = "application/json"
                    return response

                allowed_datasets_for_counts = response.json()["result"]
                request.allowed_datasets_for_counts = allowed_datasets_for_counts

        response = self.get_response(request)
        return response
