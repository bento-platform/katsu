from bento_lib.auth.permissions import Permission
from bento_lib.auth.resources import build_resource
from django.core.exceptions import PermissionDenied, ValidationError
from django.http.request import HttpRequest
from rest_framework.request import Request as DrfRequest
from typing import Iterable

from ..authz.discovery import (
    DataTypeDiscoveryPermissions,
    DiscoveryPermissionsDict,
    get_data_type_discovery_permissions,
)
from ..authz.middleware import authz_middleware
from ..authz.utils import data_req_method_to_permission
from ..chord import models as cm

from .censorship import RULES_NO_PERMISSIONS, RULES_FULL_PERMISSIONS
from .config import discovery_config
from .fields import get_public_model_name_and_field_path
from .model_lookups import PUBLIC_MODEL_NAMES_TO_DATA_TYPE
from .types import DiscoveryRules, DiscoveryConfig


def get_count_and_query_data_permissions_for_field(
    dt_permissions: DataTypeDiscoveryPermissions, field_props: dict
) -> DiscoveryPermissionsDict:
    public_model_name, _ = get_public_model_name_and_field_path(field_props["mapping"])
    field_bento_data_type = PUBLIC_MODEL_NAMES_TO_DATA_TYPE[public_model_name]
    return dt_permissions[field_bento_data_type]


async def datasets_allowed_for_request_and_data_type(
    request: DrfRequest | HttpRequest, data_type, permission_override: Permission | None = None
) -> tuple[str, ...]:
    perm = permission_override or data_req_method_to_permission(request)
    resources = [
        build_resource(project=ds.project_id, dataset=ds.identifier, data_type=data_type)
        async for ds in cm.Dataset.objects.all()
    ]
    resources_allowed = tuple(map(all, await authz_middleware.async_evaluate(request, resources, (perm,))))
    return tuple(r["dataset"] for r, rp in zip(resources, resources_allowed) if rp)


def permissions_on_public_field_set(
    fields_accessed: Iterable[str],
    dt_permissions: DataTypeDiscoveryPermissions,
) -> tuple[DiscoveryPermissionsDict, dict[str, DiscoveryPermissionsDict]]:
    dts_accessed: set[str] = set()
    field_dts: dict[str, str] = {}

    field_set = set(fields_accessed)
    queryable_fields = get_public_queryable_fields()

    for field in field_set:
        if field not in queryable_fields:
            raise ValidationError(f"Unsupported field used in query: {field}")

        mn, _ = get_public_model_name_and_field_path(queryable_fields[field]["mapping"])

        if (f_dt := PUBLIC_MODEL_NAMES_TO_DATA_TYPE.get(mn)) is not None:
            dts_accessed.add(f_dt)
            field_dts[field] = f_dt

    if not all(dt_permissions[dt]["counts"] for dt in dts_accessed):
        raise PermissionDenied()

    field_permissions: dict[str, DiscoveryPermissionsDict] = {f: dt_permissions[field_dts[f]] for f in field_set}

    return {
        "counts": all(dt_permissions[dt]["counts"] for dt in dts_accessed),
        "data": all(dt_permissions[dt]["data"] for dt in dts_accessed),
    }, field_permissions


def get_public_queryable_fields():
    search_conf = discovery_config["search"]
    field_conf = discovery_config["fields"]
    queryable_fields = {
        f"{f}": field_conf[f] for section in search_conf for f in section["fields"]
    }
    return queryable_fields


async def get_public_data_type_permissions(request: DrfRequest) -> DataTypeDiscoveryPermissions:
    return await get_data_type_discovery_permissions(
        request,

        # Collect all data types that we need permissions for to give various parts of the public overview response.
        #  - individuals & biosamples are in the 'phenopacket' data type, experiments are in the 'experiment' data type
        list(set(PUBLIC_MODEL_NAMES_TO_DATA_TYPE.values()))
    )


def get_discovery_rules_and_field_set_permissions(
    dt_permissions: DataTypeDiscoveryPermissions,
    field_set: Iterable[str] | None = None,
) -> tuple[DiscoveryRules, DiscoveryPermissionsDict, dict[str, DiscoveryPermissionsDict]]:
    if not discovery_config:
        return RULES_NO_PERMISSIONS, {"counts": False, "data": False}, {}  # no discovery allowed, use no permissions

    # -----

    queryable_fields = get_public_queryable_fields()
    all_qf_permissions, qf_permissions = permissions_on_public_field_set(
        queryable_fields.keys() if not field_set else field_set, dt_permissions)

    # -----

    if not any(all_qf_permissions.values()):  # no permissions
        rules = RULES_NO_PERMISSIONS
    elif all_qf_permissions["data"]:
        rules = RULES_FULL_PERMISSIONS
    else:
        rules = discovery_config["rules"]

    return rules, all_qf_permissions, qf_permissions


def get_config_public_and_field_set_permissions(
    dt_permissions: DataTypeDiscoveryPermissions,
    field_set: Iterable[str] | None = None,
) -> tuple[DiscoveryConfig, DiscoveryPermissionsDict, dict[str, DiscoveryPermissionsDict]]:
    """
    Gets public configuration file. Some values of this response can be updated from the base config based on the
    environment/permissions.
    """

    if not discovery_config:  # None?
        return discovery_config  # return as-is

    # overwrite rules with calculated rules based on permissions:
    rules, all_qf_permissions, qf_permissions = get_discovery_rules_and_field_set_permissions(dt_permissions, field_set)
    return {**discovery_config, "rules": rules}, all_qf_permissions, qf_permissions
