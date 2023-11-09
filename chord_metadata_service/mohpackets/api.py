import json
import logging
import os
import re
from functools import wraps
from typing import Dict, List, Optional, Type

import orjson
import yaml
from authx.auth import get_opa_datasets, is_site_admin
from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Model, Prefetch, Q
from django.http import HttpResponse, JsonResponse
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object
from ninja import Field, FilterSchema, ModelSchema, NinjaAPI, Query, Schema
from ninja.orm import create_schema
from ninja.pagination import PageNumberPagination, paginate
from ninja.parser import Parser
from ninja.renderers import BaseRenderer
from ninja.security import HttpBearer
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from chord_metadata_service.mohpackets.api_authorized import router as authorzied_router
from chord_metadata_service.mohpackets.api_discovery import router as discovery_router
from chord_metadata_service.mohpackets.utils import get_schema_url

logger = logging.getLogger(__name__)
SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


class ORJSONRenderer(BaseRenderer):
    media_type = "application/json"

    def render(self, request, data, *, response_status):
        return orjson.dumps(data)


class ORJSONParser(Parser):
    def parse_body(self, request):
        return orjson.loads(request.body)


class OPAAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            opa_secret = settings.CANDIG_OPA_SECRET
            request.has_permission = request.method in SAFE_METHODS or is_site_admin(
                request, admin_secret=opa_secret
            )
            if not request.has_permission:
                return None
            authorized_datasets = get_opa_datasets(request, admin_secret=opa_secret)
            request.authorized_datasets = authorized_datasets

        except Exception as e:
            logger.exception(f"An error occurred in OPA: {e}")
            raise Exception("Error with OPA authentication.")

        # debug message
        logger.debug(
            "Authentication completed for request '%s' with token: %s. Authorized datasets: %s. Permission: %s",
            request.get_full_path(),
            token,
            authorized_datasets,
            request.has_permission,
        )
        return token


class LocalAuth(HttpBearer):
    def authenticate(self, request, token):
        request.has_permission = request.method in SAFE_METHODS or any(
            d.get("is_admin", False)
            for d in settings.LOCAL_AUTHORIZED_DATASET
            if d["token"] == token
        )
        if not request.has_permission:
            return None

        authorized_datasets = [
            dataset
            for d in settings.LOCAL_AUTHORIZED_DATASET
            if d["token"] == token
            for dataset in d["datasets"]
        ]
        request.authorized_datasets = authorized_datasets
        # debug message
        logger.debug(
            "Authentication completed for request '%s' with token: %s. Authorized datasets: %s. Permission: %s",
            request.get_full_path(),
            token,
            authorized_datasets,
            request.has_permission,
        )

        return token


settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
# Use OPA in prod/dev environment
if "dev" in settings_module or "prod" in settings_module:
    auth = OPAAuth()
else:
    auth = LocalAuth()


api = NinjaAPI(renderer=ORJSONRenderer(), parser=ORJSONParser())
api.add_router("/authorized/", authorzied_router, auth=auth, tags=["authorized"])
api.add_router("/discovery/", discovery_router, tags=["discovery"])


@api.get("/service-info/")
def service_info(request):
    schema_url = get_schema_url()

    return JsonResponse(
        {
            "name": "katsu",
            "description": "A CanDIG clinical data service",
            "version": settings.KATSU_VERSION,
            "schema_url": schema_url,
        },
        status=200,
        safe=False,
        json_dumps_params={"indent": 2},
    )
