from django.conf import settings
from django.http import HttpResponseServerError
import requests
import json


class AuthzMiddleware:
    """
    Middleware for dataset-level authorization.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/api/phenopackets" and request.method == "GET":
            request_body = {
                "user_tokens": [],
                "path": [request.path],
                "method": request.method
            }

            if settings.CANDIG_OPA_URL:
                try:
                    response = requests.post(settings.CANDIG_OPA_URL + "/v1/data/permissions", json=request_body)
                    response.raise_for_status()
                except requests.exceptions.RequestException:
                    error_response = {
                        "error": "error getting response from authorization service"
                    }
                    response = HttpResponseServerError(json.dumps(error_response))
                    response["Content-Type"] = "application/json"
                    return response

                allowed_datasets = response.json()["datasets"]
                request.allowed_datasets = allowed_datasets

        response = self.get_response(request)
        return response
