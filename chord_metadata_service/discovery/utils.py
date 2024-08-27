from bento_lib.auth.resources import RESOURCE_EVERYTHING, build_resource
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.request import Request as DrfRequest
from typing import Iterable

from chord_metadata_service.authz.helpers import get_data_type_query_permissions
from chord_metadata_service.authz.types import (
    DataPermissionsDict, DataTypeDiscoveryPermissions, FieldDiscoveryPermissions
)
from chord_metadata_service.chord import models as cm

from .exceptions import DiscoveryConfigException
from .fields_utils import get_public_model_name_and_field_path
from .model_lookups import PUBLIC_MODEL_NAMES_TO_DATA_TYPE
from .types import DiscoveryConfig, DiscoveryFieldProps

__all__ = [
    "get_discovery",
    "get_request_discovery",
    "get_project_id_and_dataset_id_from_request",
    "get_discovery_queryable_fields",
    "get_discovery_data_type_permissions",
    "get_discovery_field_set_permissions",
]


async def _get_project_discovery(project_id: str | None = None, project: cm.Project | None = None) -> dict:
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


async def get_discovery(project_id: str | None = None, dataset_id: str | None = None) -> DiscoveryConfig:
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


def get_project_id_and_dataset_id_from_request(request: DrfRequest) -> tuple[str | None, str | None]:
    return request.query_params.get("project") or None, request.query_params.get("dataset") or None


async def get_request_discovery(request: DrfRequest) -> DiscoveryConfig:
    project_id, dataset_id = get_project_id_and_dataset_id_from_request(request)
    return await get_discovery(project_id, dataset_id)


def get_discovery_queryable_fields(discovery: DiscoveryConfig) -> dict[str, DiscoveryFieldProps]:
    field_conf = discovery["fields"]
    return {
        f"{f}": field_conf[f] for section in discovery["search"] for f in section["fields"]
    }


async def get_discovery_data_type_permissions(
    request: DrfRequest, project_id: str | None = None, dataset_id: str | None = None
) -> DataTypeDiscoveryPermissions:
    # Do here instead of inside get_data_type_query_permissions, since this getter function is specific to discovery

    if project_id is None and dataset_id is None:
        project_id, dataset_id = get_project_id_and_dataset_id_from_request(request)

    resource: dict = RESOURCE_EVERYTHING
    if project_id:
        if dataset_id:
            resource = build_resource(project_id, dataset_id)
        else:
            resource = build_resource(project_id)

    dataset_level = "dataset" in resource

    return await get_data_type_query_permissions(
        request,

        # Collect all data types that we need permissions for to give various parts of the public overview response.
        #  - individuals & biosamples are in the 'phenopacket' data type, experiments are in the 'experiment' data type
        #  - TODO: filter to just data types which are ingested?
        data_types=list(set(PUBLIC_MODEL_NAMES_TO_DATA_TYPE.values())),

        # Pass scope for permissions as resource
        resource=resource,
        dataset_level=dataset_level,
    )


def get_discovery_field_set_permissions(
    discovery: DiscoveryConfig,
    fields_accessed: Iterable[str] | None,
    dt_permissions: DataTypeDiscoveryPermissions,
) -> tuple[DataPermissionsDict, FieldDiscoveryPermissions]:
    dts_accessed: set[str] = set()
    field_dts: dict[str, str] = {}

    discovery_fields = discovery.get("fields", {})

    if not discovery_fields:
        # If no fields configured, default safe: fall back to no permissions
        return {"bool_": False, "counts": False, "data": False}, {}

    field_set = set(fields_accessed) if fields_accessed else set(discovery_fields.keys())

    for field in field_set:
        if field not in discovery_fields:
            raise ValidationError(f"Unsupported field used in query: {field}")

        mn, _ = get_public_model_name_and_field_path(discovery_fields[field]["mapping"])
        f_dt = PUBLIC_MODEL_NAMES_TO_DATA_TYPE[mn]
        dts_accessed.add(f_dt)
        field_dts[field] = f_dt

    field_permissions: FieldDiscoveryPermissions = {f: dt_permissions[field_dts[f]] for f in field_set}

    return {
        "bool_": all(dt_permissions[dt]["bool_"] for dt in dts_accessed),
        "counts": all(dt_permissions[dt]["counts"] for dt in dts_accessed),
        "data": all(dt_permissions[dt]["data"] for dt in dts_accessed),
    }, field_permissions
