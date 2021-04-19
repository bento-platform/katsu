from django.conf import settings
from django.http import HttpResponseServerError
import requests
import json

REQUEST_PATHS_TO_AUTHZ_PATHS = {"/api/phenopackets": "api/phenopackets",
                                "/api/individuals": "api/ga4gh/individuals"}


class AuthzMiddleware:
    """
    Middleware for dataset-level authorization.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in REQUEST_PATHS_TO_AUTHZ_PATHS and request.method == "GET":
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

        response = self.get_response(request)
        return response
