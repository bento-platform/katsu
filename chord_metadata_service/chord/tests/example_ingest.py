from chord_metadata_service.restapi.tests.utils import load_local_json

__all__ = [
    "EXAMPLE_INGEST_EXPERIMENT",
    "EXAMPLE_INGEST_EXPERIMENT_RESULT",
    "EXAMPLE_INGEST_PHENOPACKET",
    "EXAMPLE_INGEST_PHENOPACKET_UPDATE",
    "EXAMPLE_INGEST_EXPERIMENT_BAD_BIOSAMPLE",
    "EXAMPLE_INGEST_INVALID_EXPERIMENT",
    "EXAMPLE_INGEST_INVALID_PHENOPACKET",
    "EXAMPLE_INGEST_MULTIPLE_PHENOPACKETS",
]

EXAMPLE_INGEST_PHENOPACKET = load_local_json("example_phenopacket.json")
EXAMPLE_INGEST_PHENOPACKET_UPDATE = load_local_json("example_phenopacket_2.json")

EXAMPLE_INGEST_EXPERIMENT = load_local_json("example_experiment.json")
EXAMPLE_INGEST_EXPERIMENT_BAD_BIOSAMPLE = load_local_json("example_experiment_bad_biosample.json")
EXAMPLE_INGEST_EXPERIMENT_BAD_RESOURCE = load_local_json("example_experiment bad_resource.json")

EXAMPLE_INGEST_INVALID_EXPERIMENT = load_local_json("example_invalid_experiment.json")
EXAMPLE_INGEST_EXPERIMENT_RESULT = load_local_json("example_derived_experiment_result.json")

EXAMPLE_INGEST_INVALID_PHENOPACKET = load_local_json("example_invalid_phenopacket.json")
EXAMPLE_INGEST_MULTIPLE_PHENOPACKETS = load_local_json("example_multiple_phenopackets.json")
