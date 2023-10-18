from django.http import HttpRequest
from typing import overload

from .constants import PERMISSION_QUERY_DATA
from .middleware import authz_middleware
from .utils import create_resource

__all__ = [
    "query_permission",
    "can_query_data",
    "has_query_data_permission_for_data_types",
]


@overload
async def query_permission(request: HttpRequest, resource: dict, permission: str) -> bool:
    ...


@overload
async def query_permission(request: HttpRequest, resource: list[dict], permission: str) -> tuple[bool, ...]:
    ...


async def query_permission(
    request: HttpRequest, resource: dict | list[dict], permission: str
) -> bool | tuple[bool, ...]:
    return tuple(
        await authz_middleware.async_authz_post(request, "/policy/evaluate", {
            "requested_resource": resource,
            "required_permissions": [permission],
        })["result"]
    )


@overload
async def can_query_data(request: HttpRequest, resource: dict) -> bool:
    ...


@overload
async def can_query_data(request: HttpRequest, resource: list[dict]) -> tuple[bool, ...]:
    ...


async def can_query_data(request: HttpRequest, resource: dict | list[dict]) -> bool | tuple[bool, ...]:
    return await query_permission(request, resource, PERMISSION_QUERY_DATA)


async def has_query_data_permission_for_data_types(
    request: HttpRequest, project: str | None, dataset: str | None, data_types: list[str]
) -> list[bool]:
    has_permission: bool = await can_query_data(request, create_resource(project, dataset, None))
    return [
        # Either we have permission for all (saves many calls) or we have for a specific data type
        has_permission or (await can_query_data(request, create_resource(project, dataset, dt_id)))
        for dt_id in data_types
    ]
