from bento_lib.auth.permissions import (
    Permission,
    P_QUERY_PROJECT_LEVEL_BOOLEAN,
    P_QUERY_DATASET_LEVEL_BOOLEAN,
    P_QUERY_DATASET_LEVEL_COUNTS,
    P_QUERY_PROJECT_LEVEL_COUNTS,
    P_QUERY_DATA,
)
from bento_lib.auth.middleware.django import DjangoAuthMiddleware
from bento_lib.auth.resources import RESOURCE_EVERYTHING, build_resource
from django.http import HttpRequest
from rest_framework.request import Request

from .middleware import authz_middleware
from .types import Bools, DataTypeDiscoveryPermissions


__all__ = [
    "get_bool_permission",
    "get_counts_permission",
    "can_see_bool",
    "can_see_counts",
    "has_query_data_permission_for_data_types",
    "get_data_type_query_permissions",
]


def get_bool_permission(dataset_level: bool) -> Permission:
    return P_QUERY_DATASET_LEVEL_BOOLEAN if dataset_level else P_QUERY_PROJECT_LEVEL_BOOLEAN


def get_counts_permission(dataset_level: bool) -> Permission:
    return P_QUERY_DATASET_LEVEL_COUNTS if dataset_level else P_QUERY_PROJECT_LEVEL_COUNTS


async def _can_see_censored(
    request: HttpRequest,
    authz: DjangoAuthMiddleware,
    resources: list[dict],
    censored_permission: Permission,
) -> Bools:
    # P_QUERY_DATA as a fallback for any censored data query
    assert censored_permission in P_QUERY_DATA.gives  # must be a given permission from query:data
    return tuple(map(any, (
        await authz.async_evaluate(request, resources, (censored_permission, P_QUERY_DATA))
    )))


async def can_see_bool(request: HttpRequest, resources: list[dict], dataset_level: bool) -> Bools:
    return await _can_see_censored(request, authz_middleware, resources, get_bool_permission(dataset_level))


async def can_see_counts(request: HttpRequest, resources: list[dict], dataset_level: bool) -> Bools:
    return await _can_see_censored(request, authz_middleware, resources, get_counts_permission(dataset_level))


async def can_query_data(request: Request | HttpRequest, resource: dict) -> bool:
    return await authz_middleware.async_evaluate_one(request, resource, P_QUERY_DATA)


async def has_query_data_permission_for_data_types(
    request: Request | HttpRequest, project_id: str | None, dataset_id: str | None, data_types: list[str]
) -> Bools:
    has_permission: bool = await can_query_data(request, build_resource(project_id, dataset_id))

    if has_permission:
        return tuple([True] * len(data_types))

    resources = [build_resource(project_id, dataset_id, dt_id) for dt_id in data_types]
    res = await authz_middleware.async_evaluate(request, resources, (P_QUERY_DATA,))
    return tuple(ps[0] for ps in res)


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
