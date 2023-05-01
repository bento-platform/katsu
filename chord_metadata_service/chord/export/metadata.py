from chord_metadata_service.chord.models import Dataset, Project, Table
from chord_metadata_service.chord.workflows.metadata import WORKFLOW_CBIOPORTAL

from .cbioportal import study_export as export_cbioportal_workflow

__all__ = [
    "OBJECT_TYPE_PROJECT",
    "OBJECT_TYPE_DATASET",
    "OBJECT_TYPE_TABLE",

    "EXPORT_OBJECT_TYPE",
    "EXPORT_FORMATS",
    "EXPORT_FORMAT_FUNCTION_MAP",
    "EXPORT_FORMAT_OBJECT_TYPE_MAP",
]


OBJECT_TYPE_PROJECT = "project"
OBJECT_TYPE_DATASET = "dataset"
OBJECT_TYPE_TABLE = "table"

EXPORT_OBJECT_TYPE = {
    OBJECT_TYPE_PROJECT: {
        "model": Project
    },
    OBJECT_TYPE_DATASET: {
        "model": Dataset
    },
    OBJECT_TYPE_TABLE: {
        "model": Table
    },
}

EXPORT_FORMATS = {WORKFLOW_CBIOPORTAL}

EXPORT_FORMAT_FUNCTION_MAP = {
    WORKFLOW_CBIOPORTAL: export_cbioportal_workflow
}

EXPORT_FORMAT_OBJECT_TYPE_MAP = {
    WORKFLOW_CBIOPORTAL: {OBJECT_TYPE_DATASET}
}
