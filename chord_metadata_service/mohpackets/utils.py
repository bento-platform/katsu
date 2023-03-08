import logging

from authx.auth import get_opa_datasets
from django.conf import settings

"""
    This module contains various utility functions.
"""
logger = logging.getLogger(__name__)


def get_authorized_datasets(request):
    """
    Returns a list of datasets that the user is authorized to see.
    NOTE: this function required the OPA service to be running, otherwise it will raise an exception.
    """
    if settings.KATSU_AUTHORIZATION == "OPA" and "Authorization" in request.headers:
        opa_url = settings.CANDIG_OPA_URL
        opa_secret = settings.CANDIG_OPA_SECRET
        try:
            opa_res_datasets = get_opa_datasets(
                request, opa_url=opa_url, admin_secret=opa_secret
            )
            return opa_res_datasets
        except Exception as e:
            logging.exception(f"An error occurred in get_authorized_datasets: {e}")
            raise ValueError("Error retrieving authorized datasets")

    if (
        settings.KATSU_AUTHORIZATION == "LOCAL_SETTING_NO_AUTH"
        or "Authorization" not in request.headers
    ):
        # NOTE: THIS IS FOR LOCAL TESTING ONLY
        # If the request is not coming from auth stack (i.e. we call the API directly)
        # then we return a fake authorized dataset list.
        logger.info(
            f"No authorization header found, using default authorized datasets {settings.FAKE_AUTHORIZED_DATASETS}"
        )
        return settings.FAKE_AUTHORIZED_DATASETS

    # If none of the above, raise a ValueError
    raise ValueError("Invalid or missing authorization settings.")
