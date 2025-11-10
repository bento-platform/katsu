from asgiref.sync import async_to_sync
from rest_framework.request import Request as DrfRequest
from structlog.stdlib import BoundLogger

from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope
from chord_metadata_service.discovery.types import EntityCountOrBoolResponse
from chord_metadata_service.discovery.api_views import get_censored_entity_counts
from chord_metadata_service.discovery.utils import get_discovery_data_type_permissions


__all__ = ["get_censored_counts_for_serializer"]


@async_to_sync
async def get_censored_counts_for_serializer(
    request: DrfRequest | None,
    scope: ValidatedDiscoveryScope,
    logger: BoundLogger,
) -> EntityCountOrBoolResponse:
    # Early return for non-GET requests
    if not request or request.method not in ("GET", "HEAD", "OPTIONS"):
        logger.debug("Skipping counts computation for non-GET request")
        return {}

    # Bind scope and method to logger
    scope_repr = repr(scope)
    lg = logger.bind(
        method=request.method,
        scope_repr=scope_repr,
        request_id=getattr(request, "id", None),
    )

    try:
        dt_permissions = await get_discovery_data_type_permissions(request, scope)
        return await get_censored_entity_counts(scope, dt_permissions, lg=lg, query=None)
    except Exception as e:
        lg.warning(
            "Failed to compute entity counts for serializer, returning empty dict",
            exc_info=e,
        )
        return {}
