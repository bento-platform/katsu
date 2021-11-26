from django.conf import settings
from django.http import HttpResponseForbidden
import requests
import re
import json


class DatasetsAuthzMiddleware:
    """
    A generic middleware for dataset-level authorization.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.authorize_datasets = 'NO_DATASETS_AUTHORIZED'
        self.authorized_paths = [
            "^/api/phenopackets/?.*", "^/api/diagnoses/?.*", "^/api/diseases/?.*",
            "^/api/genes/?.*", "^/api/genomicinterpretations/?.*", "^/api/htsfiles/?.*", "^/api/individuals/?.*",
            "^/api/interpretations/?.*", "^/api/metadata/?.*", "^/api/phenopackets/?.*", "^/api/phenotypicfeatures/?.*",
            "^/api/procedures/?.*", "^/api/variants/?.*", "^/api/biosamples/?.*",
            "^/api/mcodepackets/?.*", "^/api/medicationstatements/?.*",  "^/api/geneticspecimens/?.*" ,
            "^/api/cancergeneticvariants/?.*" ,"^/api/genomicregionsstudied/?.*" ,"^/api/genomicsreports/?.*" ,"^/api/labsvital/?.*" ,
            "^/api/cancerconditions/?.*" ,"^/api/tnmstaging/?.*" ,"^/api/cancerrelatedprocedures/?.*"]

    def __call__(self, request):
        """
        You may incorporate any data source for dataset authorization.

        Note, if no datasets are authorized, you MUST set it to 'NO_DATASETS_AUTHORIZED'.

        If authorized datasets exist, set it to a comma-separated string with titles of authorized datasets.

        For example, if datasets d100 and d200 are authorized, you should set
        self.authorize_datasets = 'd100,d200'
        """

        if settings.CANDIG_AUTHORIZATION == 'OPA' and request.method == 'GET'\
            and any(re.match(path_re, request.path) for path_re in self.authorized_paths):
            if settings.CACHE_TIME != 0:
                error_response = {
                    "error": "This request failed because caching is not disabled. \
                                Please contact your system administrator for assistance."
                }
                response = HttpResponseForbidden(json.dumps(error_response))
                response["Content-Type"] = "application/json"
                return response
            token = self.get_opa_token_from_request(request.headers)
            opa_res_datasets = self.get_opa_res(token, request.path, request.method)
            if len(opa_res_datasets) == 0:
                self.authorize_datasets = 'NO_DATASETS_AUTHORIZED'
            elif type(opa_res_datasets) == tuple and opa_res_datasets[0] == "error": #  error response
                return opa_res_datasets[1]
            else:
                self.authorize_datasets = ",".join(opa_res_datasets)
            request.GET = request.GET.copy() #  Make request.GET mutable
            request.GET.update({'authorized_datasets': self.authorize_datasets})
            response = self.get_response(request)
            return response
        response = self.get_response(request)
        return response

    def get_opa_token_from_request(self, headers):
        """
        Extracts token from request's header Authorization
        """
        token = headers.get('Authorization').split()[1]
        if token is None:
            return ""
        return token

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
            response = requests.post(
                settings.CANDIG_OPA_URL + "/v1/data/permissions/datasets",
                headers={"Authorization": f"Bearer {settings.CANDIG_OPA_SECRET}"},
                json=self.get_request_body(token, path, method)
            )
            response.raise_for_status()
        except requests.exceptions.RequestException:
            error_response = {
                "error": "This request failed because we are unable to retrieve necessary info \
                                related to your account. Please contact your system administrator \
                                for assistance."
            }
            response = HttpResponseForbidden(json.dumps(error_response))
            response["Content-Type"] = "application/json"
            return ("error", response)

        allowed_datasets = response.json()["result"]

        return allowed_datasets
