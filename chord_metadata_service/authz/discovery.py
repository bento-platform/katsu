from bento_lib.auth.permissions import (
    Permission,
    P_QUERY_DATASET_LEVEL_COUNTS,
    P_QUERY_PROJECT_LEVEL_COUNTS,
    P_QUERY_DATA,
)
from bento_lib.auth.resources import RESOURCE_EVERYTHING, build_resource
from django.http import HttpRequest
from rest_framework.request import Request
from typing import TypedDict

from .middleware import authz_middleware


__all__ = [
    "get_counts_permission",
    "can_see_counts",
    "has_counts_permission_for_data_types",
    "has_counts_permission_for_data_types_bulk_resources",
    "DiscoveryPermissionsDict",
    "DataTypeDiscoveryPermissions",
    "get_data_type_discovery_permissions",
]


def get_counts_permission(dataset_level: bool) -> Permission:
    # We don't have a node-level counts permission
    return P_QUERY_DATASET_LEVEL_COUNTS if dataset_level else P_QUERY_PROJECT_LEVEL_COUNTS


async def can_see_counts(request: HttpRequest, resources: list[dict], dataset_level: bool) -> tuple[bool, ...]:
    return tuple(map(any, (
        await authz_middleware.async_evaluate(request, resources, (get_counts_permission(dataset_level), P_QUERY_DATA))
    )))


async def has_counts_permission_for_data_types(
    request: HttpRequest, project: str | None, dataset: str | None, data_types: list[str]
) -> tuple[bool, ...]:
    dataset_level: bool = dataset is not None

    if project is None:
        res_everything = (await can_see_counts(request, [RESOURCE_EVERYTHING], dataset_level))[0]
        return tuple([res_everything] * len(data_types))

    return await can_see_counts(
        request, [build_resource(project, dataset, dt_id) for dt_id in data_types], dataset_level)


async def has_counts_permission_for_data_types_bulk_resources(
    request: HttpRequest,
    resource_tuples: tuple[tuple[str | None, str | None], ...],
    data_types: list[str],
    dataset_level: bool,
):
    resources_without_dts = [build_resource(project, dataset) for project, dataset in resource_tuples]
    has_permission_by_resource: tuple[bool, ...] = await can_see_counts(request, resources_without_dts, dataset_level)

    return [
        # Either we have permission for all (saves many calls via or-shortcutting) or we have for a specific
        # data type and resource:
        [True] * len(data_types) if has_permission else (
            await can_see_counts(request, [{**resource, "data_type": dt_id} for dt_id in data_types], dataset_level)
        )
        for has_permission, resource in zip(has_permission_by_resource, resources_without_dts)
    ]


class DiscoveryPermissionsDict(TypedDict):
    counts: bool
    data: bool


DataTypeDiscoveryPermissions = dict[str, DiscoveryPermissionsDict]


async def get_data_type_discovery_permissions(
    request: Request | HttpRequest, data_types: list[str]
) -> DataTypeDiscoveryPermissions:
    # For all of these required data types, figure out if we have:
    #  a) full-response query:data permissions, and
    #  b) count-level permissions (at the project level) - will also re-check the query:data permissions currently :(

    # TODO: PROJECT PASSED IN + PROPER DATA TYPE LIST - eventually this should change based on project/dataset/etc perms
    #  query_data_perms,  # query:data permissions for each data type
    #  counts_perms,  # query:project_level_counts permissions for each data type

    p_query_counts, p_query_data = (
        await authz_middleware.async_evaluate(
            request, (RESOURCE_EVERYTHING,), (P_QUERY_PROJECT_LEVEL_COUNTS, P_QUERY_DATA)
        )
    )[0]

    # Collect these permissions, organized by data type, in a dictionary, so we can query them later:
    return {
        dt: {
            "counts": p_query_counts,
            "data": p_query_data,
        }
        for dt in data_types
    }
