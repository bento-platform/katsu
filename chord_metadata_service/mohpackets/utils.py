import logging
import os

from authx.auth import get_opa_datasets
from django.conf import settings

logger = logging.getLogger(__name__)


# def get_authorized_datasets(request):
#     """
#     Returns a list of datasets that the user is authorized to see.

#     If the Django settings module is set to a development or production environment,
#     this function retrieves the authorized datasets from the OPA service using the
#     authorization header in the request. If the OPA service is not available or if
#     the authorization fails, this function raises a ValueError.

#     If the Django settings module is set to a local environment, this function returns
#     a default list of authorized datasets from the Django settings.

#     Otherwise, this function raises a ValueError.
#     """
#     settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")

#     # Check for production or development environment
#     if "dev" in settings_module or "prod" in settings_module:
#         auth_header = request.headers.get("Authorization")
#         if not auth_header:
#             raise ValueError("No authorization header found")

#         opa_url = settings.CANDIG_OPA_URL
#         opa_secret = settings.CANDIG_OPA_SECRET
#         try:
#             authorized_datasets = get_opa_datasets(
#                 request, opa_url=opa_url, admin_secret=opa_secret
#             )
#         except Exception as e:
#             logging.exception(f"An error occurred in get_authorized_datasets: {e}")
#             raise ValueError("Error retrieving authorized datasets")

#     # Check for local environment
#     elif "local" in settings_module:
#         authorized_datasets = settings.FAKE_AUTHORIZED_DATASETS
#         logger.info(
#             f"Local settings detected, using default authorized datasets {authorized_datasets}"
#         )

#     # Invalid settings module
#     else:
#         raise ValueError("Invalid or missing authorization settings.")

#     return authorized_datasets
