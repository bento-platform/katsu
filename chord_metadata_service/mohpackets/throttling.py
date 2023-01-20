from rest_framework.throttling import SimpleRateThrottle

"""
    This module contains the custom throttling class for the MOH API.
    Most class-based API will use the built-in ScopedRateThrottle class, but
    the function-based API will use this custom throttling class.
"""


class MoHRateThrottle(SimpleRateThrottle):
    scope = "moh_rate_limit"

    def get_cache_key(self, request, view):
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }
