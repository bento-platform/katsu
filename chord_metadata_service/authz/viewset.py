from bento_lib.auth.permissions import P_QUERY_DATA, Permission, P_INGEST_DATA, P_DELETE_DATA
from rest_framework import mixins, viewsets
from rest_framework.request import Request as DrfRequest

from chord_metadata_service.discovery.scope import get_request_discovery_scope, ValidatedDiscoveryScope
from chord_metadata_service.discovery.scopeable_model import BaseScopeableModel

from .permissions import BentoDataTypePermission
from .middleware import authz_middleware

__all__ = [
    "BentoAuthzScopedModelGenericViewSet",
    "BentoAuthzScopedModelViewSet",
]


class BentoAuthzScopedModelGenericViewSet(viewsets.GenericViewSet):
    """
    An extension of the DRF generic viewset which TODO
    Security note: Subclasses MUST implement a get_queryset(...) which returns a model-scoped queryset!
    """

    data_type: str | None = None
    permission_classes = (BentoDataTypePermission,)

    @staticmethod
    async def obj_is_in_request_scope(request: DrfRequest, obj: BaseScopeableModel) -> bool:
        scope = await get_request_discovery_scope(request)
        return await obj.scope_contains_object(scope)

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
        _scope: ValidatedDiscoveryScope = scope or await get_request_discovery_scope(request)

        p: Permission | None = self.permission_from_request(request)
        if p is None:
            return False

        return await authz_middleware.async_evaluate_one(
            request, _scope.as_authz_resource(data_type=self.data_type), p, mark_authz_done=True
        )


class BentoAuthzScopedModelViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    BentoAuthzScopedModelGenericViewSet
):
    """
    This class is equivalent to the DRF viewsets.ModelViewSet class, except with our BentoAuthzModelGenericViewSet
    replacing the base viewsets.GenericViewSet. In this way, we get all the scoping / permissions helper functions.
    Security note: Subclasses MUST implement a get_queryset(...) which returns a model-scoped queryset!
    """
    pass
