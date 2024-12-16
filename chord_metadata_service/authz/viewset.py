from bento_lib.auth.permissions import P_QUERY_DATA, Permission, P_INGEST_DATA, P_DELETE_DATA
from rest_framework import mixins, viewsets
from rest_framework.request import Request as DrfRequest

from chord_metadata_service.discovery.scope import get_request_discovery_scope, INSTANCE_SCOPE, ValidatedDiscoveryScope
from chord_metadata_service.discovery.scopeable_model import BaseScopeableModel

from .permissions import BentoDataTypePermission
from .middleware import authz_middleware

__all__ = [
    "BentoAuthzModelGenericViewSet",
    "BentoAuthzModelViewSet",
]


class BentoAuthzModelGenericViewSet(viewsets.GenericViewSet):
    data_type: str | None = None
    scope_enabled: bool = False  # must be set to True in order to get correctly-scoped permissions

    permission_classes = (BentoDataTypePermission,)

    async def _get_scope_for_request(self, request: DrfRequest) -> ValidatedDiscoveryScope:
        if self.scope_enabled:
            return await get_request_discovery_scope(request)
        else:
            return INSTANCE_SCOPE

    async def obj_is_in_request_scope(self, request: DrfRequest, obj: BaseScopeableModel) -> bool:
        scope = await self._get_scope_for_request(request)
        return await obj.scope_contains_object_async(scope)

    def permission_from_request(self, request: DrfRequest) -> Permission | None:
        if self.action in ("list", "retrieve"):
            return P_QUERY_DATA
        elif self.action in ("create", "update"):
            return P_INGEST_DATA
        elif self.action == "destroy":
            return P_DELETE_DATA
        else:
            return None

    async def request_has_data_type_permissions(
            self, request: DrfRequest, scope: ValidatedDiscoveryScope | None = None
    ):
        # We MUST specifically mark view sets as scope-enabled (which means their queryset handles scope correctly);
        # otherwise, we cannot scope into a specific project/dataset and must use the whole instance as the scope.
        # Otherwise, we can could leak data from other projects/datasets.
        # TODO: there must be a better way to enforce this without manual flagging

        _scope: ValidatedDiscoveryScope = scope or await self._get_scope_for_request(request)

        p: Permission | None = self.permission_from_request(request)
        if p is None:
            return False

        return await authz_middleware.async_evaluate_one(
            request, _scope.as_authz_resource(data_type=self.data_type), p, mark_authz_done=True
        )


class BentoAuthzModelViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    BentoAuthzModelGenericViewSet
):
    pass
