from asgiref.sync import async_to_sync
from bento_lib.auth.permissions import P_DELETE_DATA, P_INGEST_DATA, P_QUERY_DATA, Permission
from django.db import transaction
from django.db.models import Model
from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.request import Request as DrfRequest

from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope, get_request_discovery_scope
from chord_metadata_service.discovery.scopeable_model import BaseScopeableModel
from chord_metadata_service.logger import logger

from .middleware import authz_middleware
from .permissions import BentoDataTypePermission

__all__ = [
    "BentoAuthzScopedModelGenericListViewSet",
    "BentoAuthzScopedModelViewSet",
]


class BentoAuthzScopedModelGenericListViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """
    An extension of the DRF generic viewset which adds utility functions for Bento Django permissions classes.
    These work together to properly implement scoped Bento permissions based on the request being made.

    <!!!>
    Security note: Subclasses MUST implement a get_queryset(...) which returns a model-scoped, request-based queryset!
    </!!!>
    """

    data_type: str | None = None
    permission_classes = (BentoDataTypePermission,)

    def get_queryset(self):
        raise NotImplementedError("Subclasses must implement scoped get_queryset")

    @staticmethod
    async def obj_is_in_request_scope(request: DrfRequest, obj: BaseScopeableModel) -> bool:
        # DiscoveryScopeException - project/dataset does not exist, or non-UUID request for a project/dataset
        #  - will be an API exception and handled by the katsu exception handler
        return await obj.scope_contains_object(await get_request_discovery_scope(request))

    def permission_from_request(self, request: DrfRequest) -> Permission | None:
        if self.action in ("list", "retrieve"):
            return P_QUERY_DATA
        elif self.action in ("create", "update", "partial_update"):
            return P_INGEST_DATA
        elif self.action == "destroy":
            return P_DELETE_DATA
        else:
            logger.error("viewset permission_from_request(...) is not implemented for action", action=self.action)
            return None

    async def request_has_data_type_permissions(
        self, request: DrfRequest, scope: ValidatedDiscoveryScope | None = None
    ):
        # DiscoveryScopeException - project/dataset does not exist, or non-UUID request for a project/dataset
        #  - will be an API exception and handled by the katsu exception handler
        scope_: ValidatedDiscoveryScope = scope or await get_request_discovery_scope(request)

        p: Permission | None = self.permission_from_request(request)
        if p is None:
            return False

        return await authz_middleware.async_evaluate_one(
            request, scope_.as_authz_resource(data_type=self.data_type), p, mark_authz_done=True
        )


class BentoAuthzScopedModelViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    BentoAuthzScopedModelGenericListViewSet,
):
    """
    This class is equivalent to the DRF viewsets.ModelViewSet class, except with our BentoAuthzModelGenericViewSet
    replacing the base viewsets.GenericViewSet. In this way, we get all the scoping / permissions helper functions.
    Security note: Subclasses MUST implement a get_queryset(...) which returns a model-scoped queryset!

    Permissions are evaluated against the scope in the query string, so writes are additionally checked to make sure
    the request body cannot reach outside that scope: every referenced object must be in scope (or not belong to any
    dataset), and the saved object itself must end up in scope (or not belong to any dataset).
    """

    async def related_object_in_scope(self, scope: ValidatedDiscoveryScope, obj: Model) -> bool:
        """
        Returns whether an object referenced by a create/update request body may be referenced under the passed scope.
        Subclasses can override this to handle related models which are not scopeable themselves.
        """
        if isinstance(obj, BaseScopeableModel):
            return await obj.scope_allows_object(scope)
        return True

    async def _check_related_objects_in_scope(self, scope: ValidatedDiscoveryScope, validated_data: dict) -> None:
        for field_name, value in validated_data.items():
            for obj in value if isinstance(value, (list, tuple)) else (value,):
                if isinstance(obj, Model) and not await self.related_object_in_scope(scope, obj):
                    # Same message as DRF's PrimaryKeyRelatedField, so out-of-scope objects look like missing ones.
                    raise ValidationError({field_name: [f'Invalid pk "{obj.pk}" - object does not exist.']})

    def _save_within_scope(self, serializer) -> None:
        scope = async_to_sync(get_request_discovery_scope)(self.request)
        async_to_sync(self._check_related_objects_in_scope)(scope, serializer.validated_data)
        with transaction.atomic():
            obj = serializer.save()
            if not async_to_sync(obj.scope_allows_object)(scope):
                raise PermissionDenied("Object would be outside of the authorized scope")  # rolls back the save

    def perform_create(self, serializer):
        self._save_within_scope(serializer)

    def perform_update(self, serializer):
        self._save_within_scope(serializer)
