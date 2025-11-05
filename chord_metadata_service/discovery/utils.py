from asgiref.sync import async_to_sync
from bento_lib.discovery import DiscoveryConfig, DiscoveryEntity
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from rest_framework.request import Request as DrfRequest
from typing import Iterable

from chord_metadata_service.authz.helpers import get_data_type_query_permissions
from chord_metadata_service.authz.types import (
    DataPermissions, DataTypeDiscoveryPermissions, FieldDiscoveryPermissions
)
from chord_metadata_service.chord.data_types import KatsuDataType
from chord_metadata_service.logger import logger

from .fields_utils import normalize_field_path_true_model
from .model_lookups import DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE, DISCOVERY_ENTITY_NAMES_TO_MODEL
from .scope import ValidatedDiscoveryScope
from .types import EntityCountOrBoolResponse

__all__ = [
    "get_discovery_data_type_permissions",
    "get_discovery_field_set_permissions",
    "extract_discovery",
    "empty_discovery",
    "get_discovery_entity_model_scoped_queryset",
    "get_censored_counts_for_serializer",
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
    """
    Given a particular discovery scope and already-resolved data type permissions for this scope, as well as a list of
    field IDs that match what is in the discovery config [or, if this is None, all fields in the discovery config], this
    checks which data type is being accessed after resolving nested access and builds a dictionary of
    {field id: DataPermissions}.
    Returns a tuple of (
        DataPermissions for accessing EVERY field, i.e., field1 AND field2 AND field3 AND ...,
        {field id: DataPermissions},
    ).
    """

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

    all_fields_permissions = DataPermissions(
        bool_=all(dt_permissions[dt].bool_ for dt in dts_accessed),
        counts=all(dt_permissions[dt].counts for dt in dts_accessed),
        data=all(dt_permissions[dt].data for dt in dts_accessed)
    )  # AND of permissions for every field, so we know if we have, e.g., boolean-level access for every field passed.
    field_permissions: FieldDiscoveryPermissions = {f: dt_permissions[field_dts[f]] for f in field_set}

    return all_fields_permissions, field_permissions


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


def get_discovery_entity_model_scoped_queryset(entity: DiscoveryEntity, scope: ValidatedDiscoveryScope) -> QuerySet:
    """
    Small utility for the semi-common usage pattern of getting a scoped queryset for a discovery entity's Django model.
    """
    return DISCOVERY_ENTITY_NAMES_TO_MODEL[entity].get_model_scoped_queryset(scope)


def get_censored_counts_for_serializer(
    request: DrfRequest, scope: ValidatedDiscoveryScope
) -> EntityCountOrBoolResponse:
    """
    Sync wrapper for getting censored entity counts from serializers.
    Wraps the async get_censored_entity_counts_async function.
    """
    from .api_views import get_censored_entity_counts_async

    @async_to_sync
    async def _get_counts():
        try:
            dt_permissions = await get_discovery_data_type_permissions(request, scope)
            lg = logger.bind(request_id=getattr(request, 'id', None))
            return await get_censored_entity_counts_async(scope, dt_permissions, query=None, lg=lg)
        except Exception as e:
            logger.warning(
                "Failed to compute entity counts for serializer, returning empty dict",
                exc_info=e,
                scope=scope,
                request_id=getattr(request, 'id', None),
            )
            return {}

    return _get_counts()
