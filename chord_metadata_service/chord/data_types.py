from chord_metadata_service.experiments.search_schemas import EXPERIMENT_SEARCH_SCHEMA
from chord_metadata_service.phenopackets.search_schemas import PHENOPACKET_SEARCH_SCHEMA
from chord_metadata_service.experiments.schemas import EXPERIMENT_RESULT_SCHEMA

__all__ = [
    "DATA_TYPE_EXPERIMENT",
    "DATA_TYPE_PHENOPACKET",
    "DATA_TYPES",
]

DATA_TYPE_EXPERIMENT = "experiment"
DATA_TYPE_PHENOPACKET = "phenopacket"
DATA_TYPE_READSET = "readset"

DATA_TYPES = {
    DATA_TYPE_EXPERIMENT: {
        "schema": EXPERIMENT_SEARCH_SCHEMA,
        "metadata_schema": {
            "type": "object",  # TODO
        },
    },
    DATA_TYPE_PHENOPACKET: {
        "schema": PHENOPACKET_SEARCH_SCHEMA,
        "metadata_schema": {
            "type": "object",  # TODO
        }
    },
    DATA_TYPE_READSET: {
        "schema": {
            "file_format": EXPERIMENT_RESULT_SCHEMA["properties"]["file_format"]
        },
        "metadata_schema": {
            "type": "object"
        }
    }
}
