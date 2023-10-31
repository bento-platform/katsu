import logging
import os
import re

import yaml
from authx.auth import get_opa_datasets, is_site_admin
from django.conf import settings
from django.core.cache import cache
from ninja.security import HttpBearer

logger = logging.getLogger(__name__)

SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


class TokenAuthentication(HttpBearer):
    def authenticate(self, request, token):
        try:
            opa_secret = settings.CANDIG_OPA_SECRET
            authorized_datasets = get_opa_datasets(request, admin_secret=opa_secret)
            request.authorized_datasets = authorized_datasets
            request.has_permission = request.method in SAFE_METHODS or is_site_admin(
                request, admin_secret=opa_secret
            )
        except Exception as e:
            logger.exception(f"An error occurred in OPA: {e}")
            raise Exception("Error with OPA authentication.")


class LocalAuthentication(HttpBearer):
    def authenticate(self, request, token):
        authorized_datasets = [
            dataset
            for d in settings.LOCAL_AUTHORIZED_DATASET
            if d["token"] == token
            for dataset in d["datasets"]
        ]
        request.authorized_datasets = authorized_datasets

        request.has_permission = request.method in SAFE_METHODS or any(
            d.get("is_admin", False)
            for d in settings.LOCAL_AUTHORIZED_DATASET
            if d["token"] == token
        )

        return token


def get_schema_url():
    """
    Retrieve the schema URL either from cached or by parsing a YAML file.
    It first checks if the URL is cached in "schema_url".
    If not cached, it reads the YAML file and extracts the URL from the "description".
    """

    schema_url = cache.get("schema_url")
    url_pattern = r"https://[^\s]+"  # get everything after https

    if schema_url is None:
        try:
            with open(
                "chord_metadata_service/mohpackets/docs/schema.yml", "r"
            ) as yaml_file:
                data = yaml.safe_load(yaml_file)
                desc_str = data["info"]["description"]
                schema_url = re.search(url_pattern, desc_str).group()
                # Cache the schema_version so we won't read it each time
                cache.set("schema_url", schema_url)
        except Exception as e:
            logger.debug(
                f"An error occurred while fetching the schema URL. Details: {str(e)}"
            )
            schema_url = None
    return schema_url
