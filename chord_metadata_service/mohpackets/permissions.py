from django.conf import settings
from rest_framework.permissions import BasePermission, SAFE_METHODS
from authx.auth import is_site_admin

"""
    This module contains custom permission classes for the API.
    It works with the ModelViewSet class in api_views.py.
    By default, API endpoints allow full access without authentication, but we
    can make them a bit more secure by only allow superusers to make changes, and
    non-superusers to only read.
"""


class CanDIGAdminOrReadOnly(BasePermission):
    """
    Allow full access to CanDIG admins. This means that they can make changes.
    Allow access to anyone only for the “read-only” methods: GET, HEAD or OPTIONS.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            if settings.CANDIG_AUTHORIZATION == "OPA":
                opa_url = settings.CANDIG_OPA_URL
                opa_secret = settings.CANDIG_OPA_SECRET
                opa_site_admin = settings.CANDIG_OPA_SITE_ADMIN_KEY
                return is_site_admin(
                    request,
                    opa_url=opa_url,
                    admin_secret=opa_secret,
                    site_admin_key=opa_site_admin,
                )
            return False
