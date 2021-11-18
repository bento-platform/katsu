from django.conf import settings
from django.http import HttpResponseForbidden
import jwt
import requests
import re


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
        # TODO: Get authorized datasets from a data source.
        
        if settings.CANDIG_AUTHORIZATION == 'something':
            # Do something
        
            self.authorize_datasets = 'NO_DATASETS_AUTHORIZED'
            
            request.GET = request.GET.copy() # Make request.GET mutable
            request.GET.update({'authorized_datasets': self.authorize_datasets})
            response = self.get_response(request)
            return response


