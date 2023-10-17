from .constants import RESOURCE_EVERYTHING


__all__ = [
    "create_resource",
]


def create_resource(project: str | None, dataset: str | None, data_type: str | None) -> dict:
    resource = RESOURCE_EVERYTHING
    if project:
        resource = {"project": project}
        if dataset:
            resource["dataset"] = dataset
        if data_type:
            resource["data_type"] = data_type
    return resource
