from __future__ import annotations

import re

from collections import defaultdict
from django.db.models import F
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response
from typing import Any

from chord_metadata_service.phenopackets.models import Biosample

__all__ = [
    "transform_keys",
    "computed_property",
    "remove_computed_properties",
    "get_biosamples_with_experiment_details",
    "build_experiments_by_subject",
    "response_as_attachment",
    "attachment_content_disposition",
    "response_optionally_as_attachment",
]


COMPUTED_PROPERTY_PREFIX = "__"
FILENAME_REPLACE_PATTERN = re.compile(r"[\\/:*?\"<>|]")


def camel_case_field_names(string) -> str:
    """ Function to convert snake_case field names to camelCase """
    # Capitalize every part except the first
    return "".join(
        part.title() if i > 0 else part
        for i, part in enumerate(string.split("_"))
    )


# TODO: Typing: generics
def transform_keys(obj: Any) -> Any:
    """
    The function validates against DATS schemas that use camelCase.
    It iterates over a dict and changes all keys in nested objects to camelCase.
    """

    if isinstance(obj, list):
        return [transform_keys(i) for i in obj]

    if isinstance(obj, dict):
        return {
            camel_case_field_names(key): transform_keys(value)
            for key, value in obj.items()
        }

    return obj


def computed_property(name: str):
    """
    Takes a name and returns it prefixed with "__"
    """
    return COMPUTED_PROPERTY_PREFIX + name


def remove_computed_properties(data: dict[str, Any]) -> dict[str, Any]:
    """
    Removes computed properties from an extra_properties dictionary.
    Computed extra_properties start with "__" and should never be ingested.
    """
    if data:
        return {k: v for k, v in data.items() if not k.startswith(COMPUTED_PROPERTY_PREFIX)}
    return data


def get_biosamples_with_experiment_details(subject_ids):
    """
    The function returns a queryset where each entry represents a biosample obtained from a subject, along with
    details of any associated experiment. If a biosample does not have an associated experiment, the experiment
    details are returned as None.
    """
    biosamples_exp_tissue_details = (
        Biosample.objects
        .filter(phenopackets__subject_id__in=subject_ids)
        .values(
            subject_id=F("phenopackets__subject_id"),
            biosample_id=F("id"),
            experiment_id=F("experiments__id"),
            experiment_type=F("experiments__experiment_type"),
            study_type=F("experiments__study_type"),
            tissue_id=F("sampled_tissue__id"),
            tissue_label=F("sampled_tissue__label")
        )
    )
    return biosamples_exp_tissue_details


def build_experiments_by_subject(biosamples_experiments_details: list[dict]) -> dict[str, list[dict]]:
    experiments_with_biosamples = defaultdict(list)
    for b in biosamples_experiments_details:
        experiments_with_biosamples[b["subject_id"]].append({
            "biosample_id": b["biosample_id"],
            "sampled_tissue": {
                "id": b["tissue_id"],
                "label": b["tissue_label"]
            },
            "experiment": {
                "experiment_id": b["experiment_id"],
                "experiment_type": b["experiment_type"],
                "study_type": b["study_type"]
            }
        })
    return experiments_with_biosamples


def response_as_attachment(request: DrfRequest) -> bool:
    """
    Helper function for processing the as_attachment query parameter, for consistent behaviour when returning JSON
    responses as file attachments.
    """
    return request.query_params.get("attachment", "").strip().lower() in ("1", "true", "yes")


def attachment_content_disposition(filename: str) -> dict[str, str]:
    filename_safe = FILENAME_REPLACE_PATTERN.sub("_", filename)
    return {"Content-Disposition": f"attachment; filename=\"{filename_safe}\""}


def response_optionally_as_attachment(request: DrfRequest, data, filename: str) -> Response:
    return Response(data, headers=attachment_content_disposition(filename) if response_as_attachment(request) else {})
