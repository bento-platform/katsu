from asgiref.sync import async_to_sync
from bento_lib.auth.permissions import P_DELETE_DATA, P_INGEST_DATA, P_QUERY_DATA, Permission
from django.db import transaction
from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request as DrfRequest

from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope, get_request_discovery_scope
from chord_metadata_service.discovery.scopeable_model import BaseScopeableModel
from chord_metadata_service.logger import logger
from chord_metadata_service.restapi.serializers import WRITE_SCOPE_CONTEXT_KEY

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
    Writes must also stay inside the request scope, since permissions are only checked against it.
    """

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action in ("create", "update", "partial_update"):
            context[WRITE_SCOPE_CONTEXT_KEY] = async_to_sync(get_request_discovery_scope)(self.request)
        return context

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    # DRF drops the (scoped) prefetch cache after a save, so re-fetch through the scoped queryset.
    def _use_scoped_instance_for_response(self, serializer, obj: BaseScopeableModel) -> None:
        if (scoped_obj := self.get_queryset().filter(pk=obj.pk).first()) is not None:
            serializer.instance = scoped_obj

    def perform_create(self, serializer):
        obj = serializer.save()
        scope = serializer.context[WRITE_SCOPE_CONTEXT_KEY]
        if not type(obj).get_referenceable_queryset(scope).filter(pk=obj.pk).exists():
            raise PermissionDenied("Object would be outside of the authorized scope")  # rolls back the transaction
        self._use_scoped_instance_for_response(serializer, obj)

    def perform_update(self, serializer):
        obj = serializer.save()
        scope = serializer.context[WRITE_SCOPE_CONTEXT_KEY]
        if not type(obj).get_model_scoped_queryset(scope).filter(pk=obj.pk).exists():
            raise PermissionDenied("Object would be outside of the authorized scope")  # rolls back the transaction
        self._use_scoped_instance_for_response(serializer, obj)
