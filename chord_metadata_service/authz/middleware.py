import re

from bento_lib.auth.middleware.django import DjangoAuthMiddleware
from django.conf import settings

from ..logger import logger

__all__ = [
    "authz_middleware",
    "AuthzMiddleware",
]

pattern_get = re.compile(r"^GET$")

# --- List of patterns to apply authz middleware to --------------------------------------------------------------------
#  - Note: as we gradually roll out authz across Katus, this list will expand. Anything not covered here is assumed to
#          be protected by the gateway.
include_pattern_public = (
    re.compile(r"^(GET|POST|PUT|DELETE)$"),
    re.compile(r"^/api/(projects|datasets|public|public_overview|public_search_fields|public_rules)$"),
)
include_pattern_workflows = (pattern_get, re.compile(r"^(/workflows$|/workflows/)"))
include_pattern_si = (pattern_get, re.compile(r"^/service-info"))
include_pattern_schemas = (pattern_get, re.compile(r"^/schemas/.+$"))
include_pattern_schema_types = (pattern_get, re.compile(r"^/extra_properties_schema_types$"))
# ----------------------------------------------------------------------------------------------------------------------

authz_middleware = DjangoAuthMiddleware(
    bento_authz_service_url=settings.BENTO_AUTHZ_SERVICE_URL,
    debug_mode=settings.DEBUG,
    enabled=settings.BENTO_AUTHZ_ENABLED,
    include_request_patterns=(
        include_pattern_public,
        include_pattern_workflows,
        include_pattern_si,
        include_pattern_schemas,
        include_pattern_schema_types,
    ),
    logger=logger,
)

AuthzMiddleware = authz_middleware.make_django_middleware()
