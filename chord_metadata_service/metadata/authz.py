from bento_lib.auth.middleware.django import DjangoAuthMiddleware
from django.conf import settings

from ..logger import logger

__all__ = [
    "authz_middleware",
]

authz_middleware = DjangoAuthMiddleware(
    bento_authz_service_url=settings.BENTO_AUTHZ_SERVICE_URL,
    debug_mode=settings.DEBUG,
    enabled=settings.BENTO_AUTHZ_ENABLED,
    logger=logger,
)

AuthzMiddleware = authz_middleware.make_django_middleware()
