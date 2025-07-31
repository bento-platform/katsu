from bento_lib.discovery import DiscoveryConfig
from django.core.exceptions import ValidationError
from rest_framework.request import Request as DrfRequest
from typing import Iterable

from chord_metadata_service.authz.helpers import get_data_type_query_permissions
from chord_metadata_service.authz.types import (
    DataPermissions, DataTypeDiscoveryPermissions, FieldDiscoveryPermissions
)
from chord_metadata_service.chord.data_types import KatsuDataType

from .fields_utils import normalize_field_path_true_model
from .model_lookups import DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE
from .scope import ValidatedDiscoveryScope

__all__ = [
    "get_discovery_data_type_permissions",
    "get_discovery_field_set_permissions",
    "extract_discovery",
    "empty_discovery",
]


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
        data_types=list(set(DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE.values())),

        # Pass scope for permissions as resource
        resource=resource,
        dataset_level=dataset_level,
    )


def get_discovery_field_set_permissions(
    discovery_or_scope: DiscoveryConfig | ValidatedDiscoveryScope,
    fields_accessed: Iterable[str] | None,
    dt_permissions: DataTypeDiscoveryPermissions,
) -> tuple[DataPermissions, FieldDiscoveryPermissions]:

    discovery_fields = extract_discovery(discovery_or_scope).fields

    if not discovery_fields:
        # If no fields configured, default safe: fall back to no permissions
        return DataPermissions(bool_=False, counts=False, data=False), {}

    dts_accessed: set[KatsuDataType] = set()
    field_dts: dict[str, KatsuDataType] = {}

    # field_set here is a set of strings, which are the *discovery field IDs/keys* (rather than mappings another ID.)
    field_set = set(fields_accessed or discovery_fields.keys())

    for field in field_set:
        if field not in discovery_fields:
            raise ValidationError(f"Unsupported field used in query: {field}")

        # need to normalize the field path before using it, to make sure we get the true data type of the access:
        f_entity, f_field_path = normalize_field_path_true_model(*discovery_fields[field].get_entity_and_field_path())

        f_dt = DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE[f_entity]

        dts_accessed.add(f_dt)
        field_dts[field] = f_dt

    field_permissions: FieldDiscoveryPermissions = {f: dt_permissions[field_dts[f]] for f in field_set}

    return DataPermissions(
        bool_=all(dt_permissions[dt].bool_ for dt in dts_accessed),
        counts=all(dt_permissions[dt].counts for dt in dts_accessed),
        data=all(dt_permissions[dt].data for dt in dts_accessed)
    ), field_permissions


def extract_discovery(discovery_or_scope: DiscoveryConfig | ValidatedDiscoveryScope) -> DiscoveryConfig:
    """
    Hacky version of a trait, essentially - extract DiscoveryConfig from an object which is either already a
    DiscoveryConfig, or is a ValidatedDiscoveryScope.
    """
    return (
        discovery_or_scope.discovery if isinstance(discovery_or_scope, ValidatedDiscoveryScope) else discovery_or_scope
    )


def empty_discovery(discovery_or_scope: DiscoveryConfig | ValidatedDiscoveryScope | None) -> bool:
    """
    Examines a discovery configuration object and determines if it's "empty-ish", i.e., doesn't have anything
    configured that would allow for discovery to actually happen.
    :param discovery_or_scope: A DiscoveryConfig Pydantic model instance, or None.
    :return: True if discovery is "empty-ish", otherwise False.
    """
    if discovery_or_scope is None:
        return True
    discovery = extract_discovery(discovery_or_scope)
    return not discovery.fields or not (discovery.overview or discovery.search)
