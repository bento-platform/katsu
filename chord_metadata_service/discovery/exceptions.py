__all__ = [
    "DiscoveryScopeException",
    "DiscoveryEmptyException",
]

from rest_framework import status
from rest_framework.exceptions import APIException


class DiscoveryScopeException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Error validating discovery scope (does not exist)"
    default_code = "bad_request"

    def __init__(self, dataset_id: str | None = None, project_id: str | None = None, *args) -> None:
        self.dataset_id = dataset_id
        self.project_id = project_id

        message = "Error validating discovery scope: {0} {1} does not exist."
        if dataset_id and project_id:
            message = message.format("project-dataset", f"({project_id}, {dataset_id}) pair")
        elif dataset_id:
            message = message.format("dataset", dataset_id)
        elif project_id:
            message = message.format("project", project_id)
        self.message = {"message": message}

        super().__init__(*args, detail=message)


class DiscoveryEmptyException(Exception):
    pass
