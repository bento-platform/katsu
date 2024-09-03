import uuid

from bento_lib.auth.resources import build_resource
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.request import Request as DrfRequest
from typing import Iterable

from chord_metadata_service.authz.helpers import get_data_type_query_permissions
from chord_metadata_service.authz.types import (
    DataPermissionsDict, DataTypeDiscoveryPermissions, FieldDiscoveryPermissions
)
from chord_metadata_service.chord import models as cm

from .exceptions import DiscoveryScopeException
from .fields_utils import get_public_model_name_and_field_path
from .model_lookups import PUBLIC_MODEL_NAMES_TO_DATA_TYPE
from .types import DiscoveryConfig, DiscoveryFieldProps, EmptyConfig

__all__ = [
    "ValidatedDiscoveryScope",
    "get_discovery_scope",
    "get_request_discovery_scope",
    "get_discovery_queryable_fields",
    "get_discovery_data_type_permissions",
    "get_discovery_field_set_permissions",
]


class ValidatedDiscoveryScope:
    """
    Contains discovery scope information (i.e., project and dataset), as well as helper methods for accessing the
    scope's discovery configuration, Bento authorization resource representation, and IDs.

    Projects and datasets are passed into the constructor rather than IDs to allow discovery calculations *and* ensure
    the project/dataset actually exist before scope object creation, thus the name - the project and dataset's
    existences are pre-validated. Of course, a project/dataset could be deleted asynchronously elsewhere, which could
    result in this becoming invalid.
    """

    def __init__(self, project: cm.Project | None, dataset: cm.Dataset | None):
        """
        Constructor for an already-validated discovery scope - i.e., since we are getting fed project/dataset instances
        rather than just string IDs, we know these objects exist at the time of construction.
        """

        self._project = project
        self._dataset = dataset

        # Additional validation - make sure we have project set if dataset is set
        if self._dataset and not self._project:
            raise DiscoveryScopeException(dataset_id=str(self._dataset.identifier))

        # We can cache get_discovery() after the first call, since instances of this class MUST NOT be mutated.
        self._discovery: DiscoveryConfig | EmptyConfig | None = None

    @property
    def project_id(self) -> str | None:
        """
        String representation of the scope project's ID, if set.
        """
        return str(self._project.identifier) if self._project else None

    @property
    def dataset_id(self) -> str | None:
        """
        String representation of the scope dataset's ID, if set.
        """
        return str(self._dataset.identifier) if self._dataset else None

    def __repr__(self):
        return f"<ValidatedDiscoveryScope project={self.project_id} dataset={self.dataset_id}>"

    async def _get_project_discovery_or_fallback(self) -> DiscoveryConfig | EmptyConfig:
        if self._project and (d := self._project.discovery):
            return d
        else:
            # fallback on global discovery config if project is not set or has None as discovery
            return settings.CONFIG_PUBLIC

    async def _get_dataset_discovery_or_fallback(self) -> DiscoveryConfig | EmptyConfig:
        """
        Gets the dataset discovery configuration dictionary, or falls back to the project (and eventually instance) one.
        """
        if self._dataset and (d := self._dataset.discovery):
            return d
        else:
            return await self._get_project_discovery_or_fallback()

    async def get_discovery(self) -> DiscoveryConfig | EmptyConfig:
        """
        Get the discovery configuration dictionary for this scope, properly handling falling back
        (dataset -> project -> instance) as required.
        """
        if self._discovery is not None:
            return self._discovery
        else:
            d = await self._get_dataset_discovery_or_fallback()
            self._discovery = d
            return d

    def as_authz_resource(self) -> dict:
        """
        Build a Bento authorization system-compatible resource dictionary from this discovery scope.
        """
        return build_resource(self.project_id, self.dataset_id)


def _get_project_id_and_dataset_id_from_request(request: DrfRequest) -> tuple[str | None, str | None]:
    return request.query_params.get("project") or None, request.query_params.get("dataset") or None


async def _get_project_by_id(project_id: str) -> cm.Project:
    return await cm.Project.objects.filter(identifier=project_id).aget()


async def get_discovery_scope(project_id: str | None, dataset_id: str | None) -> ValidatedDiscoveryScope:
    project: cm.Project | None = None
    dataset: cm.Dataset | None = None

    is_scope_valid: bool = True

    try:
        if project_id:
            uuid.UUID(project_id)
        if dataset_id:
            uuid.UUID(dataset_id)
    except ValueError:
        # We don't want to facilitate log injection, so replace the true values with placeholders
        raise DiscoveryScopeException("<not UUID>", "<not UUID>")

    try:
        if dataset_id:
            qs = cm.Dataset.objects.filter(identifier=dataset_id)
            if project_id:
                # check if the dataset exists and belongs to the specified project if project ID is specified;
                # otherwise, infer the project from the dataset.
                qs = qs.filter(project_id=project_id)

            dataset = await qs.aget()
            project = await _get_project_by_id(dataset.project_id)

        elif project_id:
            project = await _get_project_by_id(project_id)

    except ObjectDoesNotExist:
        is_scope_valid = False

    if not is_scope_valid:
        # We've already checked these are UUIDs, so they're fine to log
        raise DiscoveryScopeException(dataset_id, project_id)

    return ValidatedDiscoveryScope(project=project, dataset=dataset)


async def get_request_discovery_scope(request: DrfRequest) -> ValidatedDiscoveryScope:
    project_id, dataset_id = _get_project_id_and_dataset_id_from_request(request)
    return await get_discovery_scope(project_id, dataset_id)


def get_discovery_queryable_fields(discovery: DiscoveryConfig) -> dict[str, DiscoveryFieldProps]:
    field_conf = discovery["fields"]
    return {
        f"{f}": field_conf[f] for section in discovery["search"] for f in section["fields"]
    }


async def get_discovery_data_type_permissions(
    request: DrfRequest, scope: ValidatedDiscoveryScope
) -> DataTypeDiscoveryPermissions:
    # Do here instead of inside get_data_type_query_permissions, since this getter function is specific to discovery

    resource: dict = scope.as_authz_resource()
    dataset_level = scope.dataset_id is not None

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
