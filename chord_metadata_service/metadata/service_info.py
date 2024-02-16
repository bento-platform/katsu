from django.conf import settings

from bento_lib.service_info.constants import SERVICE_ORGANIZATION_C3G
from bento_lib.service_info.types import GA4GHServiceInfo
from bento_lib.service_info.helpers import build_service_info

from .. import __version__
from ..logger import logger

__all__ = [
    "get_service_info",
]


# Service info according to spec https://github.com/ga4gh-discovery/ga4gh-service-info

async def get_service_info() -> GA4GHServiceInfo:
    return await build_service_info({
        "id": settings.CHORD_SERVICE_ID,
        "name": "Katsu",  # TODO: Globally unique?
        "type": settings.CHORD_SERVICE_TYPE,
        "environment": "prod",
        "description": "Clinical and phenotypic metadata service implementation based on Phenopackets schema.",
        "organization": SERVICE_ORGANIZATION_C3G,
        "contactUrl": "mailto:info@c3g.ca",
        "version": __version__,
        "bento": {
            "serviceKind": settings.BENTO_SERVICE_KIND,
            "dataService": True,
        },
    }, debug=settings.DEBUG, local=settings.BENTO_CONTAINER_LOCAL, logger=logger)
