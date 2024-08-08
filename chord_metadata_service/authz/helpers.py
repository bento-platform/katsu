from bento_lib.auth.permissions import (
    Permission,
    P_QUERY_PROJECT_LEVEL_BOOLEAN,
    P_QUERY_DATASET_LEVEL_BOOLEAN,
    P_QUERY_DATASET_LEVEL_COUNTS,
    P_QUERY_PROJECT_LEVEL_COUNTS,
    P_QUERY_DATA,
)
from bento_lib.auth.resources import RESOURCE_EVERYTHING
from django.http import HttpRequest
from rest_framework.request import Request

from .middleware import authz_middleware
from .types import DataTypeDiscoveryPermissions


__all__ = [
    "get_bool_permission",
    "get_counts_permission",
    "get_data_type_query_permissions",
]


def get_bool_permission(dataset_level: bool) -> Permission:
    return P_QUERY_DATASET_LEVEL_BOOLEAN if dataset_level else P_QUERY_PROJECT_LEVEL_BOOLEAN


def get_counts_permission(dataset_level: bool) -> Permission:
    return P_QUERY_DATASET_LEVEL_COUNTS if dataset_level else P_QUERY_PROJECT_LEVEL_COUNTS


async def get_data_type_query_permissions(
    request: Request | HttpRequest,
    data_types: list[str],
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
    return {
        dt: {
            "bool_": p_query_bool,
            "counts": p_query_counts,
            "data": p_query_data,
        }
        for dt in data_types
    }
