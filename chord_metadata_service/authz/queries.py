from bento_lib.auth.permissions import P_QUERY_DATA
from bento_lib.auth.resources import build_resource
from django.http import HttpRequest
from rest_framework.request import Request
from typing import overload

from .middleware import authz_middleware

__all__ = [
    "Bools",
    "can_query_data",
    "has_query_data_permission_for_data_types",
]


Bools = tuple[bool, ...]


@overload
async def async_check_authz(
    request: Request | HttpRequest, requested_resource: dict, required_permissions: list[str]
) -> bool:
    ...


@overload
async def async_check_authz(
    request: Request | HttpRequest, requested_resource: list[dict], required_permissions: list[str]
) -> tuple[bool, ...]:
    ...


async def async_check_authz(
    request: Request | HttpRequest, requested_resource: dict | list[dict], required_permissions: list[str]
) -> bool | tuple[bool, ...]:
    req = request
    if isinstance(request, Request):
        # noinspection PyProtectedMember
        req = request._request

    res = (
        await authz_middleware.async_authz_post(req, "/policy/evaluate", {
            "requested_resource": requested_resource,
            "required_permissions": required_permissions,
        })
    )["result"]

    if isinstance(res, list):
        return tuple(res)

    return res


async def can_query_data(request: Request | HttpRequest, resource: dict) -> bool:
    return await authz_middleware.async_evaluate_one(request, resource, P_QUERY_DATA)


async def has_query_data_permission_for_data_types(
    request: Request | HttpRequest, project: str | None, dataset: str | None, data_types: list[str]
) -> Bools:
    has_permission: bool = await can_query_data(request, build_resource(project, dataset))

    res: list[bool] = []

    for dt_id in data_types:
        # Either we have permission for all (saves many calls) or we have for a specific data type
        res.append(has_permission or (await can_query_data(request, build_resource(project, dataset, dt_id))))

    return tuple(res)
