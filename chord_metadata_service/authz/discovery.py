import asyncio

from django.http import HttpRequest
from rest_framework.request import Request
from typing import overload, TypedDict

from .constants import PERMISSION_QUERY_PROJECT_LEVEL_COUNTS, PERMISSION_QUERY_DATASET_LEVEL_COUNTS
from .queries import query_permission, can_query_data, has_query_data_permission_for_data_types
from .utils import create_resource


__all__ = [
    "get_counts_permission",
    "can_see_counts",
    "has_counts_permission_for_data_types",
    "DiscoveryPermissionsDict",
    "DataTypeDiscoveryPermissions",
    "get_data_type_discovery_permissions",
]


def get_counts_permission(dataset_level: bool) -> str:
    if dataset_level:
        return PERMISSION_QUERY_DATASET_LEVEL_COUNTS
    return PERMISSION_QUERY_PROJECT_LEVEL_COUNTS  # We don't have a node-level counts permission


@overload
async def can_see_counts(request: HttpRequest, resource: dict, dataset_level: bool) -> bool:
    ...


@overload
async def can_see_counts(request: HttpRequest, resource: list[dict], dataset_level: bool) -> tuple[bool, ...]:
    ...


async def can_see_counts(
    request: HttpRequest, resource: dict | list[dict], dataset_level: bool
) -> bool | tuple[bool, ...]:
    # First, check if we have counts permission on either the project or dataset level, depending on the resource.
    # If we don't have a count permission, we may still have a query:data permission (no cascade) which gives us these
    # for free.

    return (
        await query_permission(request, resource, get_counts_permission(dataset_level))
        or await can_query_data(request, resource)   # or-shortcut means this only runs if it needs to be checked.
    )


async def has_counts_permission_for_data_types(
    request: HttpRequest, project: str | None, dataset: str | None, data_types: list[str]
) -> list[bool]:
    dataset_level: bool = dataset is not None

    has_permission: bool = await can_see_counts(request, create_resource(project, dataset), dataset_level)

    return [
        # Either we have permission for all (saves many calls via or-shortcutting) or we have for a specific data type:
        has_permission or await can_see_counts(request, create_resource(project, dataset, dt_id), dataset_level)
        for dt_id, can_see_counts_for_dt in data_types
    ]


async def has_counts_permission_for_data_types_bulk_resources(
    request: HttpRequest,
    resource_tuples: tuple[tuple[str | None, str | None], ...],
    data_types: list[str],
    dataset_level: bool,
):
    pass  # TODO


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

    query_data_perms, counts_perms = await asyncio.gather(
        has_query_data_permission_for_data_types(request, None, None, data_types),
        has_counts_permission_for_data_types(request, None, None, data_types),
    )

    # Collect these permissions, organized by data type, in a dictionary, so we can query them later:
    return {
        dt: {
            "counts": c_perm,
            "data": qd_perm,
        }
        for dt, qd_perm, c_perm in zip(
            data_types,  # List of data type IDs
            query_data_perms,  # query:data permissions for each data type
            counts_perms,  # query:project_level_counts permissions for each data type
        )
    }
