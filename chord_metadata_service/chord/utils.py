import asyncio

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


# Serializer context key for caching resolved discovery data type permissions. Populated in bulk by
# prefetch_discovery_permissions_for_serializer so that serializing N projects/datasets costs one authz request per
# permission level (project-level and/or dataset-level), not one per object.
DT_PERMISSIONS_CACHE_KEY = "_discovery_dt_permissions"

# Cache keys include the permission level the entry was resolved at, since project-level and dataset-level
# permissions have different meanings: (dataset_level, scope)
type DTPermissionsCacheKey = tuple[bool, ValidatedDiscoveryScope]


def _dt_permissions_cache_key(scope: ValidatedDiscoveryScope) -> DTPermissionsCacheKey:
    return scope.dataset_id is not None, scope


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

    cache: dict[DTPermissionsCacheKey, DataTypeDiscoveryPermissions] = context.setdefault(DT_PERMISSIONS_CACHE_KEY, {})

    # Group scopes not yet cached by permission level; each level is resolved with its own bulk request, so every
    # permissions object returned by a single request has the same meaning.
    missing: dict[bool, set[ValidatedDiscoveryScope]] = {}
    for scope in scopes:
        key = _dt_permissions_cache_key(scope)
        if key not in cache:
            missing.setdefault(key[0], set()).add(scope)

    if not missing:
        return

    levels = list(missing.keys())
    results = await asyncio.gather(
        *(get_discovery_data_type_permissions_bulk(request, list(missing[lvl]), lvl) for lvl in levels),
        return_exceptions=True,
    )

    for dataset_level, res in zip(levels, results):
        if isinstance(res, BaseException):
            # Leave this level unpopulated; get_censored_counts_for_serializer falls back to per-scope requests.
            logger.warning(
                "Failed to prefetch discovery permissions for serializer", dataset_level=dataset_level, exc_info=res
            )
            continue
        cache.update({(dataset_level, scope): perms for scope, perms in res.items()})


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
        dt_permissions = (context or {}).get(DT_PERMISSIONS_CACHE_KEY, {}).get(_dt_permissions_cache_key(scope))
        if dt_permissions is None:
            dt_permissions = await get_discovery_data_type_permissions(request, scope)
        return await QueryHelper(None, scope, dt_permissions, lg).get_censored_entity_counts()
    except Exception as e:
        lg.warning(
            "Failed to compute entity counts for serializer, returning empty dict",
            exc_info=e,
        )
        return {}
