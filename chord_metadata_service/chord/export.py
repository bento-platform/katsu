import logging
from chord_metadata_service.chord.ingest import WORKFLOW_CBIOPORTAL
from chord_metadata_service.chord.models import Dataset, Project, Table
from .export_cbio import study_export as export_cbioportal_workflow

logger = logging.getLogger(__name__)

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
