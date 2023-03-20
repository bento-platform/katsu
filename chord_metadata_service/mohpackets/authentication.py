import logging

from authx.auth import get_opa_datasets
from django.conf import settings
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)


class TokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth:
            raise exceptions.AuthenticationFailed("Authorization required")
        else:
            # opa_url = settings.CANDIG_OPA_URL
            opa_secret = settings.CANDIG_OPA_SECRET
            # opa_url = "http://docker.localhost:8181"
            # opa_secret = "IWyF4ST38829tuyxLYyYQ"
            # Call the get_opa_datasets function to get the authorized datasets
            try:
                # authorized_datasets = get_opa_datasets(
                #     request, opa_url=opa_url, admin_secret=opa_secret
                # )
                # todo: see why this didn't work
                authorized_datasets = get_opa_datasets(request, admin_secret=opa_secret)
            except Exception as e:
                logger.exception(
                    f"An error occurred in OPA get_authorized_datasets: {e}"
                )
                raise AuthenticationFailed(
                    f"Error retrieving authorized datasets from OPA."
                )

            # Check if the user is authorized to access any datasets.
            # By default, user has 2 or 5 datasets, so it has to be more than 5.
            if len(authorized_datasets) < 6:
                # todo: put this in the log
                logger.exception(
                    f"Retrieved {authorized_datasets}. "
                    "User should have access to additional datasets. "
                    "Either token is expired or user is not authorized."
                )
                raise Exception(f"User is not authorized to access any datasets. ")
            else:
                # add dataset to request
                request.authorized_datasets = authorized_datasets
                return None


class LocalAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth:
            raise exceptions.AuthenticationFailed("Authorization required")
        username = auth[1].decode("utf-8")
        # get authorized datasets from local settings
        authorized_datasets = [
            d["datasets"]
            for d in settings.LOCAL_AUTHORIZED_DATASET
            if d["username"] == username
        ]
        if not authorized_datasets:
            raise Exception(f"User {username} not authorized to access any datasets.")
        # add dataset to request so we can access it in views
        request.authorized_datasets = authorized_datasets[0]
        return None


class TokenScheme(OpenApiAuthenticationExtension):
    target_class = TokenAuthentication
    name = "tokenAuth"
    match_subclasses = True
    priority = -1

    def get_security_definition(self, auto_schema):
        return build_bearer_security_scheme_object(
            header_name="Authorization",
            token_prefix="Bearer",
        )


class LocalAuthScheme(OpenApiAuthenticationExtension):
    target_class = LocalAuthentication
    name = "localAuth"

    def get_security_definition(self, auto_schema):
        return build_bearer_security_scheme_object(
            header_name="Authorization",
            token_prefix="Bearer",
        )
