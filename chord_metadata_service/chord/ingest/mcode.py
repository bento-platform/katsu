import json

from chord_metadata_service.mcode.mcode_ingest import ingest_mcodepacket
from chord_metadata_service.mcode.parse_fhir_mcode import parse_bundle

from .logger import logger
from .utils import get_output_or_raise, map_if_list, workflow_file_output_to_path


def ingest_mcode_fhir_workflow(workflow_outputs, dataset_id):
    with workflow_file_output_to_path(get_output_or_raise(workflow_outputs, "json_document")) as json_doc_path:
        logger.info(f"Attempting ingestion of MCODE FIHR from path: {json_doc_path}")
        with open(json_doc_path, "r") as jf:
            json_data = json.load(jf)

    mcodepacket = parse_bundle(json_data)
    return ingest_mcodepacket(mcodepacket, dataset_id)


def ingest_mcode_workflow(workflow_outputs, dataset_id):
    with workflow_file_output_to_path(get_output_or_raise(workflow_outputs, "json_document")) as json_doc_path:
        logger.info(f"Attempting ingestion of MCODE from path: {json_doc_path}")
        with open(json_doc_path, "r") as jf:
            json_data = json.load(jf)

    return map_if_list(ingest_mcodepacket, json_data, dataset_id)
