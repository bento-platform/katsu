import logging
import os
import re
from enum import Enum
from functools import wraps
from typing import Dict, List, Optional, Type

import orjson
import yaml
from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Model, Prefetch, Q
from django.http import HttpResponse
from ninja import Field, FilterSchema, ModelSchema, NinjaAPI, Query, Schema
from ninja.orm import create_schema
from ninja.pagination import PageNumberPagination, paginate
from ninja.parser import Parser
from ninja.renderers import BaseRenderer
from ninja.security import HttpBearer

from chord_metadata_service.mohpackets.models import (
    Biomarker,
    Chemotherapy,
    Comorbidity,
    Donor,
    Exposure,
    FollowUp,
    HormoneTherapy,
    Immunotherapy,
    PrimaryDiagnosis,
    Program,
    Radiation,
    SampleRegistration,
    Specimen,
    Surgery,
    Treatment,
)

logger = logging.getLogger(__name__)


SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


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


def list_to_enum(enum_name, value_list):
    enum_dict = {}
    for item in value_list:
        enum_member_name = item.upper().replace(" ", "_")
        enum_dict[enum_member_name] = item
    return Enum(enum_name, enum_dict)
