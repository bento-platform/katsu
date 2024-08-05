import re

from bento_lib.auth.middleware.django import DjangoAuthMiddleware
from django.conf import settings

from ..logger import logger

__all__ = [
    "authz_middleware",
    "AuthzMiddleware",
]

pattern_get = re.compile(r"^GET$")

include_pattern_public = (
    re.compile(r"^(GET|POST)$"),
    re.compile(r"^/api/(projects|public|public_overview|public_search_fields|public_dataset|public_rules)$"),
)
include_pattern_workflows = (pattern_get, re.compile(r"^(/workflows$|/workflows/)"))
include_pattern_si = (pattern_get, re.compile(r"^/service-info"))

authz_middleware = DjangoAuthMiddleware(
    bento_authz_service_url=settings.BENTO_AUTHZ_SERVICE_URL,
    debug_mode=settings.DEBUG,
    enabled=settings.BENTO_AUTHZ_ENABLED,
    include_request_patterns=(include_pattern_public, include_pattern_workflows, include_pattern_si),
    logger=logger,
)

AuthzMiddleware = authz_middleware.make_django_middleware()
