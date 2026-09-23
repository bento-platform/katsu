from bento_lib.auth.permissions import (
    P_QUERY_DATA,
    P_QUERY_DATASET_LEVEL_BOOLEAN,
    P_QUERY_DATASET_LEVEL_COUNTS,
    P_QUERY_PROJECT_LEVEL_BOOLEAN,
    P_QUERY_PROJECT_LEVEL_COUNTS,
    Permission,
)
from bento_lib.auth.resources import RESOURCE_EVERYTHING
from django.http import HttpRequest
from rest_framework.request import Request

from chord_metadata_service.chord.data_types import KatsuDataType

from .middleware import authz_middleware
from .types import DataPermissions, DataTypeDiscoveryPermissions

__all__ = [
    "get_bool_permission",
    "get_counts_permission",
    "get_data_type_query_permissions",
    "get_data_type_query_permissions_bulk",
]


def get_bool_permission(dataset_level: bool) -> Permission:
    return P_QUERY_DATASET_LEVEL_BOOLEAN if dataset_level else P_QUERY_PROJECT_LEVEL_BOOLEAN


def get_counts_permission(dataset_level: bool) -> Permission:
    return P_QUERY_DATASET_LEVEL_COUNTS if dataset_level else P_QUERY_PROJECT_LEVEL_COUNTS


async def get_data_type_query_permissions(
    request: Request | HttpRequest,
    data_types: list[KatsuDataType],
    resource: dict | None = None,
    dataset_level: bool = False,
) -> DataTypeDiscoveryPermissions:
    # For all of these required data types, figure out if we have:
    #  a) full-response query:data permissions, and
    #  b) count-level permissions (at the project level) - will also re-check the query:data permissions currently :(
    #  c) bool-level permissions (at the project level) - will also re-check the query:data permissions currently :(

    bool_permission = get_bool_permission(dataset_level)
    counts_permission = get_counts_permission(dataset_level)

    p_query_bool, p_query_counts, p_query_data = (
        await authz_middleware.async_evaluate(
            request, (resource or RESOURCE_EVERYTHING,), (bool_permission, counts_permission, P_QUERY_DATA)
        )
    )[0]

    # Collect these permissions, organized by data type, in a dictionary, so we can query them later:
    #  - TODO: data type resources instead?
    return {dt: DataPermissions(bool_=p_query_bool, counts=p_query_counts, data=p_query_data) for dt in data_types}


async def get_data_type_query_permissions_bulk(
    request: Request | HttpRequest,
    data_types: list[KatsuDataType],
    resources: list[tuple[dict, bool]],
) -> list[DataTypeDiscoveryPermissions]:
    """
    Bulk version of get_data_type_query_permissions, which evaluates permissions for many (resource, dataset_level)
    pairs in a single request to the authorization service rather than one request per resource.
    Returns a list of DataTypeDiscoveryPermissions in the same order as the passed resources.
    """

    if not resources:
        return []

    permissions = (
        get_bool_permission(False),
        get_counts_permission(False),
        get_bool_permission(True),
        get_counts_permission(True),
        P_QUERY_DATA,
    )

    matrix = await authz_middleware.async_evaluate(request, tuple(r for r, _ in resources), permissions)

    res: list[DataTypeDiscoveryPermissions] = []
    for (_, dataset_level), (p_bool_p, p_counts_p, p_bool_d, p_counts_d, p_data) in zip(resources, matrix):
        dp = DataPermissions(
            bool_=p_bool_d if dataset_level else p_bool_p,
            counts=p_counts_d if dataset_level else p_counts_p,
            data=p_data,
        )
        res.append({dt: dp for dt in data_types})
    return res
