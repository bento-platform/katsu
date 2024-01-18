from django.conf import settings
from django.http import HttpResponseForbidden
import requests
import re
import json


class CandigAuthzMiddleware:
    """
    A generic middleware for CanDIGv2 authorization.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.authorize_datasets = 'NO_DATASETS_AUTHORIZED'

    def __call__(self, request):
        if settings.CANDIG_AUTHORIZATION == 'OPA':
            token = self.get_auth_token(request.headers)
            if self.is_authorized_get(request):
                """
                You may incorporate any data source for dataset authorization.

                Note, if no datasets are authorized, you MUST set it to 'NO_DATASETS_AUTHORIZED'.

                If authorized datasets exist, set it to a comma-separated string with titles of authorized datasets.

                For example, if datasets d100 and d200 are authorized, you should set
                self.authorize_datasets = 'd100,d200'
                """
                if settings.CACHE_TIME != 0:
                    error_response = {
                        "error": "This request failed because caching is not disabled. Please contact your system "
                                 "administrator for assistance."
                    }
                    response = HttpResponseForbidden(json.dumps(error_response))
                    response["Content-Type"] = "application/json"
                    return response
                opa_res_datasets = self.get_opa_datasets(token, request.path, request.method)
                if len(opa_res_datasets) == 0:
                    self.authorize_datasets = 'NO_DATASETS_AUTHORIZED'
                elif isinstance(opa_res_datasets, tuple) and opa_res_datasets[0] == "error":  # error response
                    return opa_res_datasets[1]
                else:
                    self.authorize_datasets = ",".join(opa_res_datasets)
                request.GET = request.GET.copy()  # Make request.GET mutable
                request.GET.update({'authorized_datasets': self.authorize_datasets})
            elif self.is_authorized_post(request):
                request.POST = request.POST.copy()  # Make request.POST mutable
                if not self.is_opa_site_admin(token):
                    error_response = {"error": "You do not have permission to POST"}
                    response = HttpResponseForbidden(json.dumps(error_response))
                    response["Content-Type"] = "application/json"
                    return response

        # if CANDIG_AUTHORIZATION is unknown, mean no authorization
        self.authorize_datasets = 'NO_DATASETS_AUTHORIZED'
        return self.get_response(request)

    def is_authorized_get(self, request):
        authorized_paths = [
            "^/api/phenopackets/?.*", "^/api/diagnoses/?.*", "^/api/diseases/?.*", "^/api/datasets/?.*",
            "^/api/genes/?.*", "^/api/genomicinterpretations/?.*", "^/api/individuals/?.*",
            "^/api/interpretations/?.*", "^/api/metadata/?.*", "^/api/phenopackets/?.*", "^/api/phenotypicfeatures/?.*",
            "^/api/procedures/?.*", "^/api/variants/?.*", "^/api/biosamples/?.*", "^/api/labsvital/?.*",
            "^/api/cancergeneticvariants/?.*", "^/api/genomicregionsstudied/?.*", "^/api/genomicsreports/?.*",
            "^/api/cancerconditions/?.*", "^/api/tnmstaging/?.*", "^/api/cancerrelatedprocedures/?.*"
        ]
        return request.method == 'GET' and any(re.match(path_re, request.path) for path_re in authorized_paths)

    def is_authorized_post(self, request):
        authorized_paths = [
            "^/api/datasets",
            "^/api/projects",
            "^/api/tables",
            "^/private/ingest"
        ]
        return request.method == 'POST' and any(re.match(path_re, request.path) for path_re in authorized_paths)

    def get_auth_token(self, headers):
        """
        Extracts token from request's header Authorization
        """
        token = headers.get('Authorization')
        if token is None:
            return ""
        else:
            return token.split()[1]

    def get_opa_datasets(self, token, path, method):
        """
        Get allowed dataset result from OPA
        """
        try:
            response = requests.post(
                settings.CANDIG_OPA_URL + "/v1/data/permissions/datasets",
                headers={"X-Opa": f"{settings.CANDIG_OPA_SECRET}"},
                json={
                    "input": {
                        "token": token,
                        "body": {
                            "path": path,
                            "method": method
                        }
                    }
                }
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

    def is_opa_site_admin(self, token):
        """
        Is the user associated with the token a site admin?
        """
        try:
            response = requests.post(
                settings.CANDIG_OPA_URL + "/v1/data/idp/" + settings.CANDIG_OPA_SITE_ADMIN_KEY,
                headers={"Authorization": f"Bearer {settings.CANDIG_OPA_SECRET}"},
                json={
                    "input": {
                        "token": token
                    }
                }
            )
            response.raise_for_status()
        except requests.exceptions.RequestException:
            return False
        if "result" in response.json():
            if response.json()["result"] is True or response.json()["result"] == "true":
                return True
        return False
