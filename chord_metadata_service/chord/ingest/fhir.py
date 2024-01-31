import json

from chord_metadata_service.restapi.fhir_ingest import (
    ingest_patients,
    ingest_observations,
    ingest_conditions,
    ingest_specimens
)

from .logger import logger
from .utils import get_output_or_raise, workflow_file_output_to_path

from typing import Callable

__all__ = [
    "ingest_fhir_workflow",
]


file_id_to_ingest_fn: dict[str, Callable] = {
    "patients": ingest_patients,
    "observations": ingest_observations,
    "conditions": ingest_conditions,
    "specimens": ingest_specimens,
}


def ingest_fhir_workflow(workflow_outputs, table_id):
    with workflow_file_output_to_path(get_output_or_raise(workflow_outputs, "patients")) as patients_path:
        logger.info(f"Attempting ingestion of patients from path: {patients_path}")
        with open(patients_path, "r") as pf:
            patients_data = json.load(pf)

    phenopacket_ids = ingest_patients(
        patients_data,
        table_id,
        workflow_outputs.get("created_by") or "Imported from file.",
    )

    for k in ("observations", "conditions", "specimens"):
        if k in workflow_outputs:
            with workflow_file_output_to_path(workflow_outputs[k]) as json_path:
                logger.info(f"Attempting ingestion of {k} from path: {json_path}")
                with open(json_path, "r") as of:
                    json_data = json.load(of)
            file_id_to_ingest_fn[k](phenopacket_ids, json_data)
