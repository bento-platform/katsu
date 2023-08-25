from chord_metadata_service.mcode.mcode_ingest import ingest_mcodepacket
from chord_metadata_service.mcode.parse_fhir_mcode import parse_bundle

from .utils import map_if_list


def ingest_mcode_fhir_workflow(json_data, dataset_id):
    mcodepacket = parse_bundle(json_data)
    return ingest_mcodepacket(mcodepacket, dataset_id)


def ingest_mcode_workflow(json_data, dataset_id):
    return map_if_list(ingest_mcodepacket, json_data, dataset_id)
