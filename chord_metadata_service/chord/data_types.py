from django.conf import settings
from typing import NewType

from chord_metadata_service.experiments.search_schemas import EXPERIMENT_SEARCH_SCHEMA
from chord_metadata_service.phenopackets.search_schemas import PHENOPACKET_SEARCH_SCHEMA

__all__ = [
    "KatsuDataType",
    "DATA_TYPE_EXPERIMENT",
    "DATA_TYPE_PHENOPACKET",
    "DATA_TYPES",
]


# Define a new type wrapper used only for Katsu "data types" (phenopacket/experiment). The goal here is to make
# functions which take in these values as a parameter more explicit in their type signatures.
KatsuDataType = NewType("KatsuDataType", str)

DATA_TYPE_EXPERIMENT = KatsuDataType("experiment")
DATA_TYPE_PHENOPACKET = KatsuDataType("phenopacket")

DATA_TYPES = {
    DATA_TYPE_EXPERIMENT: {
        "label": "Experiments",
        "queryable": True,
        "schema": EXPERIMENT_SEARCH_SCHEMA,
        "metadata_schema": {
            "type": "object",  # TODO
        },
    },
    DATA_TYPE_PHENOPACKET: {
        "label": settings.KATSU_PHENOPACKET_LABEL,
        "queryable": True,
        "schema": PHENOPACKET_SEARCH_SCHEMA,
        "metadata_schema": {
            "type": "object",  # TODO
        },
    },
}
