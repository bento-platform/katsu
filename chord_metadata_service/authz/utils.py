from bento_lib.auth import permissions as p
from django.core.exceptions import PermissionDenied
from django.http.request import HttpRequest
from rest_framework.request import Request as DrfRequest
from .middleware import authz_middleware

__all__ = [
    "data_req_method_to_permission",
]


def data_req_method_to_permission(request: DrfRequest | HttpRequest) -> p.Permission:
    match request.method:
        case "GET":
            return p.P_QUERY_DATA
        case "POST" | "PUT" | "PATCH":
            return p.P_INGEST_DATA
        case "DELETE":
            return p.P_DELETE_DATA
        case _:
            authz_middleware.mark_authz_done(request)
            raise PermissionDenied()
