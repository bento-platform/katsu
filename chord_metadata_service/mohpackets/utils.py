import requests
from django.conf import settings
from authx.auth import get_opa_datasets

"""
    This module contains various utility functions.
"""

def get_access_token():
    """
    Returns the access token from the request.
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
    }

    data = {
        "client_id": "local_candig",
        "client_secret": "BujuRwQrtEYrqRdncioKsyQekyifeAUm",
        "grant_type": "password",
        "username": "user1",
        "password": "w8yp5YvCuEDMNbSxwEweA",
        "scope": "openid",
    }

    response = requests.post(
        "http://docker.localhost:8080/auth/realms/candig/protocol/openid-connect/token",
        headers=headers,
        data=data,
    )

    token = response.json()["access_token"]
    return token


def get_authorized_datasets(request):
    """
    Returns a list of datasets that the user is authorized to see.
    NOTE: this function required the OPA service to be running, otherwise it will return an empty list.
    """
    if settings.CANDIG_AUTHORIZATION == "OPA":
        opa_url = settings.CANDIG_OPA_URL
        opa_secret = settings.CANDIG_OPA_SECRET
        try:
            opa_res_datasets = get_opa_datasets(
                request, opa_url=opa_url, admin_secret=opa_secret
            )
            return opa_res_datasets
        except Exception as e:
            print(e)
        
    else:
        # FOR DEBUG ONLY, REMOVE THIS WHEN DONE
        opa_url = "http://localhost:8181"
        opa_secret = "fnMt6IyEFwPxlVYjSjzilA"
        access_token = get_access_token()
        # put the access token in the request header
        request.META["HTTP_AUTHORIZATION"] = "Bearer " + access_token
        # change the path info to the path of the OPA endpoint
        request.path = "/katsu/api/mcodepackets"

        try:
            opa_res_datasets = get_opa_datasets(
                request, opa_url=opa_url, admin_secret=opa_secret
            )
            print(opa_res_datasets)
            return opa_res_datasets
        except Exception as e:
            print(e)

    return []