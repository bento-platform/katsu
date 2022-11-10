from django.conf import settings
from django.http import HttpResponseForbidden
import requests
import re
import json
import authx.auth


class CandigAuthzMiddleware:
    """
    A generic middleware for CanDIGv2 authorization.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.authorize_datasets = 'NO_DATASETS_AUTHORIZED'

    def __call__(self, request):
        if settings.CANDIG_AUTHORIZATION == 'OPA':
            opa_url = settings.CANDIG_OPA_URL
            opa_secret = settings.CANDIG_OPA_SECRET
            opa_site_admin = settings.CANDIG_OPA_SITE_ADMIN_KEY

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
                opa_res_datasets = authx.auth.get_opa_datasets(request, opa_url, opa_secret)
                if len(opa_res_datasets) == 0:
                    self.authorize_datasets = 'NO_DATASETS_AUTHORIZED'
                elif type(opa_res_datasets) == tuple and opa_res_datasets[0] == "error":  # error response
                    return opa_res_datasets[1]
                else:
                    self.authorize_datasets = ",".join(opa_res_datasets)
                request.GET = request.GET.copy()  # Make request.GET mutable
                request.GET.update({'authorized_datasets': self.authorize_datasets})
            elif self.is_authorized_post(request):
                request.POST = request.POST.copy()  # Make request.POST mutable
                if not authx.auth.is_site_admin(request, opa_url, opa_secret, site_admin_key=opa_site_admin):
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
            "^/api/genes/?.*", "^/api/genomicinterpretations/?.*", "^/api/htsfiles/?.*", "^/api/individuals/?.*",
            "^/api/interpretations/?.*", "^/api/metadata/?.*", "^/api/phenopackets/?.*", "^/api/phenotypicfeatures/?.*",
            "^/api/procedures/?.*", "^/api/variants/?.*", "^/api/biosamples/?.*", "^/api/labsvital/?.*",
            "^/api/mcodepackets/?.*", "^/api/medicationstatements/?.*",  "^/api/geneticspecimens/?.*",
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
