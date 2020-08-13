from django.conf import settings
from django.http import HttpResponseForbidden
import requests


# TODO: replace this hacky stuff with more robust solution
APPLICABLE_ENDPOINTS = [
    '/api/individuals',
    '/api/diseases',
    '/api/phenotypicfeatures'
]


class CandigAuthzMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.INSIDE_CANDIG and self.is_applicable_endpoint(request):
            # TODO: unpack the JWT and get access level
            access_level = 4

            try:
                allowed = self.query_opa(request, access_level)
            except requests.exceptions.RequestException:
                return HttpResponseForbidden()

            if allowed:
                response = self.get_response(request)
            else:
                return HttpResponseForbidden()
        else:
            response = self.get_response(request)

        return response

    def is_applicable_endpoint(self, request):
        if any(request.path == endpoint for endpoint in APPLICABLE_ENDPOINTS):
            return True
        else:
            return False

    def query_opa(self, request, access_level):
        if not settings.CANDIG_OPA_URL:
            return False

        params = {
            "input": {
                "path": request.path,
                "method": request.method,
                "access_level": access_level
            }
        }

        url = f"{settings.CANDIG_OPA_URL}/v1/data/metadata"

        res = requests.post(url, json=params)
        res.raise_for_status()

        data = res.json()

        if 'result' in data and 'allow' in data['result']:
            return data['result']['allow']
        else:
            return False
