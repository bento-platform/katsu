from typing import Type

from bento_lib.discovery import DiscoveryEntity
from chord_metadata_service.chord.data_types import KatsuDataType, DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.experiments import models as exp_models
from chord_metadata_service.patients import models as patient_models
from chord_metadata_service.phenopackets import models as pheno_models

from .scopeable_model import BaseScopeableModel

__all__ = [
    "DISCOVERY_ENTITY_NAMES_TO_MODEL",
    "DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE",
]

DISCOVERY_ENTITY_NAMES_TO_MODEL: dict[DiscoveryEntity, Type[BaseScopeableModel]] = {
    "phenopacket": pheno_models.Phenopacket,
    "individual": patient_models.Individual,
    "biosample": pheno_models.Biosample,
    "experiment": exp_models.Experiment,
}

DISCOVERY_ENTITY_NAMES_TO_DATA_TYPE: dict[DiscoveryEntity, KatsuDataType] = {
    "phenopacket": DATA_TYPE_PHENOPACKET,
    "individual": DATA_TYPE_PHENOPACKET,
    "biosample": DATA_TYPE_PHENOPACKET,
    "experiment": DATA_TYPE_EXPERIMENT,
}
