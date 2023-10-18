from django.http import HttpRequest
from rest_framework.request import Request

from .constants import RESOURCE_EVERYTHING


__all__ = [
    "create_resource",
]


def create_resource(project: str | None = None, dataset: str | None = None, data_type: str | None = None) -> dict:
    resource = RESOURCE_EVERYTHING
    if project:
        resource = {"project": project}
        if dataset:
            resource["dataset"] = dataset
        if data_type:
            resource["data_type"] = data_type
    return resource
