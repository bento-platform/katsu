__all__ = [
    "RESOURCE_EVERYTHING",
    "PERMISSION_QUERY_DATA",
    "PERMISSION_DELETE_DATA",
    "PERMISSION_QUERY_DATASET_LEVEL_COUNTS",
    "PERMISSION_QUERY_PROJECT_LEVEL_COUNTS",
]

# TODO: this should be a shared module in bento_lib

RESOURCE_EVERYTHING = {"everything": True}
PERMISSION_QUERY_DATA = "query:data"
PERMISSION_DELETE_DATA = "delete:data"

PERMISSION_QUERY_DATASET_LEVEL_COUNTS = "query:dataset_level_counts"
PERMISSION_QUERY_PROJECT_LEVEL_COUNTS = "query:project_level_counts"
