from django.http import HttpRequest

from .constants import (
    PERMISSION_QUERY_DATA,
    PERMISSION_QUERY_PROJECT_LEVEL_COUNTS,
    PERMISSION_QUERY_DATASET_LEVEL_COUNTS,
)
from .middleware import authz_middleware
from .utils import create_resource


__all__ = [
    "get_counts_permission",
    "can_see_counts",
    "has_counts_permission_for_data_types",
]


def get_counts_permission(dataset_level: bool) -> str:
    if dataset_level:
        return PERMISSION_QUERY_DATASET_LEVEL_COUNTS
    return PERMISSION_QUERY_PROJECT_LEVEL_COUNTS  # We don't have a node-level counts permission


async def can_see_counts(request: HttpRequest, resource: dict) -> bool:
    return await authz_middleware.async_authz_post(request, "/policy/evaluate", {
        "requested_resource": resource,
        "required_permissions": [get_counts_permission(resource.get("dataset") is not None)],
    })["result"] or (
        # If we don't have a count permission, we may still have a query:data permission (no cascade)
        await authz_middleware.async_authz_post(request, "/policy/evaluate", {
            "requested_resource": resource,
            "required_permissions": [PERMISSION_QUERY_DATA],
        })["result"]
    )


async def has_counts_permission_for_data_types(
    request: HttpRequest, project: str, dataset: str, data_types: list[str]
) -> list[bool]:
    has_permission: bool = await can_see_counts(request, create_resource(project, dataset, None))

    return [
        # Either we have permission for all (saves many calls) or we have for a specific data type
        has_permission or (await can_see_counts(request, create_resource(project, dataset, dt_id)))
        for dt_id in data_types
    ]
