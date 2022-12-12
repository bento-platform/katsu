from django.conf import settings
from rest_framework.permissions import BasePermission, SAFE_METHODS

"""
    This module contains custom permission classes for the API.
    It works with the ModelViewSet class in api_views.py.
    By default, API endpoints allow full access without authentication, but we
    can make them a bit more secure by only allow superusers to make changes, and
    non-superusers to only read.
"""

        
class CanDIGUser(BasePermission):
    """
        Allow access to anyone only for the “read-only” methods: GET, HEAD or OPTIONS.
        Assumed that the user is already authenticated through Tyk since this is 
        a protected endpoint.
    """
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS 
        )

class CanDIGAdmin(BasePermission):
    """
        Allow full access to CanDIG admins. This means that they can make changes.
    """
    def has_permission(self, request, view):
        # TODO: How do we check for admin status from the request?
        return True