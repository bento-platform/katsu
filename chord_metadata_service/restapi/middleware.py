from django.conf import settings
from django.http import HttpResponseForbidden
import requests


# TODO: replace this hacky stuff with more robust solution
APPLICABLE_ENDPOINTS = frozenset({
    '/api/individuals',
    '/api/diseases',
    '/api/phenotypicfeatures'
})


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

            if not allowed:
                return HttpResponseForbidden()

        return self.get_response(request)

    def is_applicable_endpoint(self, request):
        return request.path in APPLICABLE_ENDPOINTS

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

        return data.get('result', {}).get('allow', False)
