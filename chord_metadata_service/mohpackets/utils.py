from authx.auth import get_opa_datasets
from django.conf import settings

from chord_metadata_service.mohpackets.models import Program

"""
    This module contains various utility functions.
"""


def get_authorized_datasets(request):
    """
    Returns a list of datasets that the user is authorized to see.
    NOTE: this function required the OPA service to be running, otherwise it will return an empty list.
    """
    if settings.CANDIG_AUTHORIZATION == "OPA" and "Authorization" in request.headers:
        # NOTE: We assume the request comes from Tyk and it should include
        # Authorization header with special path for katsu.
        opa_url = settings.CANDIG_OPA_URL
        opa_secret = settings.CANDIG_OPA_SECRET
        try:
            opa_res_datasets = get_opa_datasets(
                request, opa_url=opa_url, admin_secret=opa_secret
            )
            return opa_res_datasets
        except Exception as e:
            print(f"Error at get_authorized_datasets: {e}")

    elif settings.CANDIG_AUTHORIZATION == "LOCAL_SETTING_NO_AUTH":
        # NOTE: this setup is for local development only.
        # It also makes testing a  bit easier.
        # We can add some logic to filter out the datasets that not authorized to see
        # For example: only authorized to see the first half of the datasets.
        # You can also overwrite this to return the datasets you want to see.
        # For example: return ["dataset1", "dataset2"]
        opa_res_datasets = Program.objects.all().values_list("name", flat=True)
        opa_res_datasets = opa_res_datasets[: len(opa_res_datasets) // 2]
        return opa_res_datasets

    return []
