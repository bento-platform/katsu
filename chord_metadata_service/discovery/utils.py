from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.request import Request as DrfRequest

from chord_metadata_service.discovery.exceptions import DiscoveryConfigException
from chord_metadata_service.discovery.types import DiscoveryConfig
from ..chord import models as cm

__all__ = [
    "get_request_discovery"
]


async def _get_project_discovery(project_id: str = None, project: cm.Project = None) -> dict:
    if not project and project_id:
        # retrieve project by ID if not provided
        project = await cm.Project.objects.aget(identifier=project_id)
    if not project.discovery:
        # fallback on global discovery config if project has none
        return settings.CONFIG_PUBLIC
    return project.discovery


async def _get_dataset_discovery(dataset_id: str) -> dict:
    dataset = await cm.Dataset.objects.aget(identifier=dataset_id)
    if not dataset.discovery:
        project = await cm.Project.objects.aget(datasets=dataset_id)
        return await _get_project_discovery(project=project)
    return dataset.discovery


async def get_discovery(project_id: str = None, dataset_id: str = None) -> DiscoveryConfig:
    if dataset_id and project_id:
        # check if the dataset belongs to the project
        is_scope_valid = await cm.Dataset.objects.filter(
            identifier=dataset_id,
            project__identifier=project_id,
        ).aexists()
        if not is_scope_valid:
            raise DiscoveryConfigException(dataset_id, project_id)
    try:
        if dataset_id:
            # get dataset's discovery config if dataset_id is passed
            return await _get_dataset_discovery(dataset_id)
        elif project_id:
            # get project's discovery config if project_id is passed and dataset_id is not
            return await _get_project_discovery(project_id=project_id)
    except ObjectDoesNotExist:
        raise DiscoveryConfigException(dataset_id, project_id)
    # fallback to config.json when no dataset or project is in the request
    return settings.CONFIG_PUBLIC


async def get_request_discovery(request: DrfRequest) -> DiscoveryConfig:
    dataset_id = request.query_params.get("dataset")
    project_id = request.query_params.get("project")
    return await get_discovery(project_id, dataset_id)
