import json

from chord_metadata_service.restapi.fhir_ingest import (
    ingest_patients,
    ingest_observations,
    ingest_conditions,
    ingest_specimens
)

from .logger import logger
from .utils import get_output_or_raise, workflow_file_output_to_path

__all__ = [
    "ingest_fhir_workflow",
]


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

    if "observations" in workflow_outputs:
        with workflow_file_output_to_path(workflow_outputs["observations"]) as observations_path:
            logger.info(f"Attempting ingestion of observations from path: {observations_path}")
            with open(observations_path, "r") as of:
                observations_data = json.load(of)
        ingest_observations(phenopacket_ids, observations_data)

    if "conditions" in workflow_outputs:
        with workflow_file_output_to_path(workflow_outputs["conditions"]) as conditions_path:
            logger.info(f"Attempting ingestion of conditions from path: {conditions_path}")
            with open(conditions_path, "r") as cf:
                conditions_data = json.load(cf)
        ingest_conditions(phenopacket_ids, conditions_data)

    if "specimens" in workflow_outputs:
        with workflow_file_output_to_path(workflow_outputs["specimens"]) as specimens_path:
            logger.info(f"Attempting ingestion of specimens from path: {specimens_path}")
            with open(specimens_path, "r") as sf:
                specimens_data = json.load(sf)
        ingest_specimens(phenopacket_ids, specimens_data)
