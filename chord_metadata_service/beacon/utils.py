from django.conf import settings

from rest_framework.request import Request
from rest_framework.response import Response

from bento_lib.service_info.constants import SERVICE_ORGANIZATION_C3G
from bento_lib.service_info.types import GA4GHServiceInfo
from bento_lib.service_info.helpers import build_service_info

from .. import __version__
from ..logger import logger

def reverse_domain_beacon_id(domain):
    return ".".join(reversed(domain.split("."))) + ".beacon"


# can deduplicate with metadata.get_service_info
# should be synchronous
async def get_service_info() -> GA4GHServiceInfo:
    return await build_service_info(
        {
            "id": reverse_domain_beacon_id(settings.SERVICE_URL_BASE_PATH),
            "name": "Bento Beacon",
            "type": settings.BEACON_SERVICE_TYPE,
            "organization": SERVICE_ORGANIZATION_C3G,
            "contactUrl": "mailto:info@c3g.ca",
            "version": __version__,
            # no longer a distinct bento service
            # "bento": {
            #     "serviceKind": "beacon",
            # },
        },
        debug=settings.DEBUG,
        local=settings.BENTO_CONTAINER_LOCAL,
        logger=logger,
    )


async def get_beacon_format_service_info():
    info = await get_service_info()
    s = {
        "id": info["id"],
        "name": info["name"],
        "environment": info["environment"],
        "organization": info["organization"],
        "apiVersion": settings.BEACON_VERSION,
        "version": __version__,
    }

    return s



# optional fields
# description 
# version (of this implementation)
# welcomeUrl
# alternativeUrl
# createDateTime
# updateDateTime
# info (object with any additional info)
