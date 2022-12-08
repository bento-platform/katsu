from django.conf import settings

from chord_metadata_service.experiments.search_schemas import EXPERIMENT_SEARCH_SCHEMA
from chord_metadata_service.phenopackets.search_schemas import PHENOPACKET_SEARCH_SCHEMA
from chord_metadata_service.mcode.schemas import MCODE_SCHEMA
from chord_metadata_service.experiments.schemas import EXPERIMENT_RESULT_SCHEMA

__all__ = [
    "DATA_TYPE_EXPERIMENT",
    "DATA_TYPE_EXPERIMENT_RESULT",
    "DATA_TYPE_PHENOPACKET",
    "DATA_TYPE_MCODEPACKET",
    "DATA_TYPE_READSET",
    "DATA_TYPES",
]

DATA_TYPE_EXPERIMENT = "experiment"
DATA_TYPE_EXPERIMENT_RESULT = "experiment_result"
DATA_TYPE_PHENOPACKET = "phenopacket"
DATA_TYPE_MCODEPACKET = "mcodepacket"
DATA_TYPE_READSET = "readset"

DATA_TYPES = {
    DATA_TYPE_EXPERIMENT: {
        "label": "Experiments",
        "schema": EXPERIMENT_SEARCH_SCHEMA,
        "metadata_schema": {
            "type": "object",  # TODO
        },
    },
    DATA_TYPE_PHENOPACKET: {
        "label": settings.KATSU_PHENOPACKET_LABEL,
        "schema": PHENOPACKET_SEARCH_SCHEMA,
        "metadata_schema": {
            "type": "object",  # TODO
        },
    },
    # De-listed 2022-12-08 - David L
    # DATA_TYPE_MCODEPACKET: {
    #     "schema": MCODE_SCHEMA,
    #     "metadata_schema": {
    #         "type": "object",  # TODO
    #     }
    # },
    DATA_TYPE_READSET: {
        "label": "Readsets",
        "schema": {
            "file_format": EXPERIMENT_RESULT_SCHEMA["properties"]["file_format"]
        },
        "metadata_schema": {
            "type": "object"
        }
    },
    DATA_TYPE_EXPERIMENT_RESULT: {
        "label": "Experiment Results",
        "schema": EXPERIMENT_RESULT_SCHEMA,
        "metadata_schema": {
            "type": "object"
        }
    }
}
