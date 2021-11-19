from django.conf import settings
from django.http import HttpResponseForbidden
from django.http.response import HttpResponseServerError
import jwt
import requests
import re
import json


class CandigAuthzMiddleware:
    """
    A generic middleware for dataset-level authorization.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.authorize_datasets = 'NO_DATASETS_AUTHORIZED'
        self.authorized_paths = [
            "^/api/phenopackets/?.*", "^/api/datasets/?.*", "^/api/diagnoses/?.*", "^/api/diseases/?.*",
            "^/api/genes/?.*", "^/api/genomicinterpretations/?.*", "^/api/htsfiles/?.*", "^/api/individuals/?.*",
            "^/api/interpretations/?.*", "^/api/metadata/?.*", "^/api/phenopackets/?.*", "^/api/phenotypicfeatures/?.*", 
            "^/api/procedures/?.*", "^/api/variants/?.*", "^/api/biosamples/?.*"]

    def __call__(self, request):
        """
        You may incorporate any data source for dataset authorization.

        Note, if no datasets are authorized, you MUST set it to 'NO_DATASETS_AUTHORIZED'.

        If authorized datasets exist, set it to a comma-separated string with titles of authorized datasets.

        For example, if datasets d100 and d200 are authorized, you should set
        self.authorize_datasets = 'd100,d200'
        """
        
        if settings.CANDIG_AUTHORIZATION == 'OPA':
            if settings.CACHE_TIME != 0:
                error_response = {
                    "error": "cache time needs to be zero to be secure"
                }
                response = HttpResponseServerError(json.dumps(error_response))
                response["Content-Type"] = "application/json"
                return response
            token = self.get_opa_token_from_request(request.headers)
            opa_res_datasets = self.get_opa_res(token, request.path, request.method)
            if len(opa_res_datasets) == 0:
                self.authorize_datasets = 'NO_DATASETS_AUTHORIZED'
            else:
                self.authorize_datasets = ",".join(opa_res_datasets)
            request.GET = request.GET.copy() # Make request.GET mutable
            request.GET.update({'authorized_datasets': self.authorize_datasets})
            response = self.get_response(request)
            return response
        response = self.get_response(request)
        return response

    def get_opa_token_from_request(self, headers):
        """
        Extracts token from request's header X-CANDIG-LOCAL-OIDC
        """
        token = headers.get("X-CANDIG-LOCAL-OIDC")
        if token == None:
            return ""
        return token.strip('"')

    def get_request_body(self, token, path, method):
        """
        Returns request body required to query OPA
        """
        return {
                "input": {
                    "token": token,
                    "body": {
                        "path": path,
                        "method": method
                    }
                }
            }

    def get_opa_res(self, token, path, method):
        """
        Get allowed dataset result from OPA
        """
        try:
            response = requests.post(settings.CANDIG_OPA_URL +
                                         "/v1/data/permissions/datasets",
                                         headers={"Authorization": f"Bearer {settings.CANDIG_PERMISSIONS_SECRET}"},
                                         json=self.get_request_body(token, path, method),
                                         verify=settings.CANDIG_ROOT_CA)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            error_response = {
                "error": "error getting response from authorization service"
            }
            response = HttpResponseServerError(json.dumps(error_response))
            response["Content-Type"] = "application/json"
            return ("error", response)

        allowed_datasets = response.json()["result"]

        return allowed_datasets

