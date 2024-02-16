from typing import Callable

from chord_metadata_service.chord.data_types import DATA_TYPE_EXPERIMENT, DATA_TYPE_PHENOPACKET
from chord_metadata_service.chord.ingest.experiments import ingest_experiments_workflow, validate_experiment
from chord_metadata_service.chord.ingest.phenopackets import ingest_phenopacket_workflow, validate_phenopacket

__all__ = [
    "DATA_TYPE_TO_VALIDATOR_FN",
    "DATA_TYPE_TO_INGESTION_FN",
]


DATA_TYPE_TO_VALIDATOR_FN: dict[str, Callable] = {
    DATA_TYPE_EXPERIMENT: validate_experiment,
    DATA_TYPE_PHENOPACKET: validate_phenopacket,
}

DATA_TYPE_TO_INGESTION_FN: dict[str, Callable] = {
    DATA_TYPE_EXPERIMENT: ingest_experiments_workflow,
    DATA_TYPE_PHENOPACKET: ingest_phenopacket_workflow,
}
