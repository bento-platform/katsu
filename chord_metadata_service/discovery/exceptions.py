__all__ = [
    "DiscoveryConfigException"
]


class DiscoveryConfigException(Exception):

    def __init__(self, dataset_id: str | None = None, project_id: str | None = None, *args: object) -> None:
        self.dataset_id = dataset_id
        self.project_id = project_id

        message = "Error retrieving {0} scoped discovery config: {0} {1} does not exist."
        if dataset_id and project_id:
            message = message.format("project-dataset", f"({project_id}, {dataset_id}) pair")
        elif dataset_id:
            message = message.format("dataset", dataset_id)
        elif project_id:
            message = message.format("project", project_id)
        self.message = {"message": message}

        super().__init__(*args)
