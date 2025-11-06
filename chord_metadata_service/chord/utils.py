from asgiref.sync import async_to_sync
from rest_framework.request import Request as DrfRequest

from chord_metadata_service.logger import logger
from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope
from chord_metadata_service.discovery.types import EntityCountOrBoolResponse
from chord_metadata_service.discovery.api_views import get_censored_entity_counts_async
from chord_metadata_service.discovery.utils import get_discovery_data_type_permissions


@async_to_sync
async def get_censored_counts_for_serializer(
    request: DrfRequest, scope: ValidatedDiscoveryScope
) -> EntityCountOrBoolResponse:
    try:
        dt_permissions = await get_discovery_data_type_permissions(request, scope)
        lg = logger.bind(request_id=getattr(request, "id", None))
        return await get_censored_entity_counts_async(scope, dt_permissions, query=None, lg=lg)
    except Exception as e:
        logger.warning(
            "Failed to compute entity counts for serializer, returning empty dict",
            exc_info=e,
            scope=scope,
            request_id=getattr(request, "id", None),
        )
        return {}
