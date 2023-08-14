import logging
import os

from authx.auth import is_site_admin
from django.conf import settings
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import SAFE_METHODS, BasePermission

logger = logging.getLogger(__name__)
"""
    This module contains custom permission classes for the API.
    By default, only allow superusers (site_admin) to make changes, and
    non-superusers to only read.
"""


class CanDIGAdminOrReadOnly(BasePermission):
    """
    The has_permission method determines if the user has permission to perform
    the requested operation.

    If the requested is a safe method (GET, HEAD or OPTIONS), returns True.
    If dev or prod environment, it checks if the user is a site admin.
    Local environment always returns True.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
            if "dev" in settings_module or "prod" in settings_module:
                opa_secret = settings.CANDIG_OPA_SECRET
                try:
                    is_admin = is_site_admin(
                        request,
                        admin_secret=opa_secret,
                    )
                    return is_admin
                except Exception as e:
                    logger.exception(f"An error occurred in OPA is_site_admin: {e}")
                    raise Exception("Error checking roles from OPA.")
            elif "local" in settings_module:
                auth = get_authorization_header(request).split()
                if not auth:
                    raise AuthenticationFailed("Authorization required")
                token = auth[1].decode("utf-8")
                is_admin = None
                for d in settings.LOCAL_AUTHORIZED_DATASET:
                    if d["token"] == token:
                        is_admin = d["is_admin"]
                        break
                if is_admin:
                    return True
            return False
