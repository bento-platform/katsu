from bento_lib.discovery.models.config import DiscoveryConfig
from bento_lib.discovery.models.fields import FieldDefinition
from django.core.exceptions import ValidationError
from rest_framework.request import Request as DrfRequest
from typing import Iterable

from chord_metadata_service.authz.helpers import get_data_type_query_permissions
from chord_metadata_service.authz.types import (
    DataPermissionsDict, DataTypeDiscoveryPermissions, FieldDiscoveryPermissions
)

from .fields_utils import get_public_model_name_and_field_path
from .model_lookups import PUBLIC_MODEL_NAMES_TO_DATA_TYPE
from .scope import ValidatedDiscoveryScope

__all__ = [
    "get_discovery_queryable_fields",
    "get_discovery_data_type_permissions",
    "get_discovery_field_set_permissions",
    "empty_discovery",
]


def get_discovery_queryable_fields(discovery: DiscoveryConfig) -> dict[str, FieldDefinition]:
    """
    Return only field definitions which are used in the search portion of the discovery configuration.
    """
    return {f: discovery.fields[f] for section in discovery.search for f in section.fields}


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

    discovery_fields = discovery.fields

    if not discovery_fields:
        # If no fields configured, default safe: fall back to no permissions
        return {"bool_": False, "counts": False, "data": False}, {}

    field_set = set(fields_accessed) if fields_accessed else set(discovery_fields.keys())

    for field in field_set:
        if field not in discovery_fields:
            raise ValidationError(f"Unsupported field used in query: {field}")

        mn, _ = get_public_model_name_and_field_path(discovery_fields[field].mapping)
        f_dt = PUBLIC_MODEL_NAMES_TO_DATA_TYPE[mn]
        dts_accessed.add(f_dt)
        field_dts[field] = f_dt

    field_permissions: FieldDiscoveryPermissions = {f: dt_permissions[field_dts[f]] for f in field_set}

    return {
        "bool_": all(dt_permissions[dt]["bool_"] for dt in dts_accessed),
        "counts": all(dt_permissions[dt]["counts"] for dt in dts_accessed),
        "data": all(dt_permissions[dt]["data"] for dt in dts_accessed),
    }, field_permissions


def empty_discovery(discovery: DiscoveryConfig | None) -> bool:
    return discovery is None or not discovery.fields or not (discovery.overview or discovery.search)
