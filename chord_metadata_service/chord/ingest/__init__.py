from chord_metadata_service.chord.workflows import metadata as wm

from .experiments import ingest_experiments_workflow
from .phenopackets import ingest_phenopacket_workflow

from typing import Callable

__all__ = [
    "WORKFLOW_INGEST_FUNCTION_MAP",
]

WORKFLOW_INGEST_FUNCTION_MAP: dict[str, Callable] = {
    wm.WORKFLOW_EXPERIMENTS_JSON: ingest_experiments_workflow,
    wm.WORKFLOW_PHENOPACKETS_JSON: ingest_phenopacket_workflow,
}
