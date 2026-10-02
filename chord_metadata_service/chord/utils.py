from asgiref.sync import async_to_sync
from rest_framework.request import Request as DrfRequest
from structlog.stdlib import BoundLogger

from chord_metadata_service.authz.types import DataTypeDiscoveryPermissions
from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope
from chord_metadata_service.discovery.types import EntityCountOrBoolResponse
from chord_metadata_service.discovery.api_views import QueryHelper
from chord_metadata_service.discovery.utils import (
    get_discovery_data_type_permissions,
    get_discovery_data_type_permissions_bulk,
)


__all__ = [
    "prefetch_discovery_permissions_for_serializer",
    "get_censored_counts_for_serializer",
]


# Serializer context key for caching resolved discovery data type permissions, keyed by scope. Populated in bulk by
# prefetch_discovery_permissions_for_serializer so that serializing N projects/datasets costs one authz request, not N.
DT_PERMISSIONS_CACHE_KEY = "_discovery_dt_permissions"


def _counts_request(request: DrfRequest | None) -> bool:
    return bool(request) and request.method in ("GET", "HEAD", "OPTIONS")


@async_to_sync
async def prefetch_discovery_permissions_for_serializer(
    context: dict,
    scopes: list[ValidatedDiscoveryScope],
    logger: BoundLogger,
) -> None:
    request = context.get("request")
    if not _counts_request(request):
        return

    cache: dict[ValidatedDiscoveryScope, DataTypeDiscoveryPermissions] = context.setdefault(
        DT_PERMISSIONS_CACHE_KEY, {}
    )
    missing = list({s for s in scopes if s not in cache})
    if not missing:
        return

    try:
        cache.update(await get_discovery_data_type_permissions_bulk(request, missing))
    except Exception as e:
        # Leave the cache unpopulated; get_censored_counts_for_serializer falls back to per-scope permission requests.
        logger.warning("Failed to prefetch discovery permissions for serializer", exc_info=e)


@async_to_sync
async def get_censored_counts_for_serializer(
    request: DrfRequest | None,
    scope: ValidatedDiscoveryScope,
    logger: BoundLogger,
    context: dict | None = None,
) -> EntityCountOrBoolResponse:
    # Early return for non-GET requests
    if not _counts_request(request):
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
        dt_permissions = (context or {}).get(DT_PERMISSIONS_CACHE_KEY, {}).get(scope)
        if dt_permissions is None:
            dt_permissions = await get_discovery_data_type_permissions(request, scope)
        return await QueryHelper(None, scope, dt_permissions, lg).get_censored_entity_counts()
    except Exception as e:
        lg.warning(
            "Failed to compute entity counts for serializer, returning empty dict",
            exc_info=e,
        )
        return {}
