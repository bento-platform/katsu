DATASET_PREFETCH = ("additional_resources",)

PROJECT_PREFETCH = ("project_schemas", "datasets", *(f"datasets__{p}" for p in DATASET_PREFETCH))
