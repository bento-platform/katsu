from typing import Type

from bento_lib.discovery import DiscoveryEntity
from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.experiments import models as exp_models
from chord_metadata_service.patients import models as patient_models
from chord_metadata_service.phenopackets import models as pheno_models

from .scopeable_model import BaseScopeableModel

__all__ = [
    "PUBLIC_MODEL_NAMES_TO_MODEL",
    "PUBLIC_MODEL_NAMES_TO_DATA_TYPE",
]

PUBLIC_MODEL_NAMES_TO_MODEL: dict[DiscoveryEntity, Type[BaseScopeableModel]] = {
    "phenopacket": pheno_models.Phenopacket,
    "individual": patient_models.Individual,
    "biosample": pheno_models.Biosample,
    "experiment": exp_models.Experiment,
}

PUBLIC_MODEL_NAMES_TO_DATA_TYPE: dict[DiscoveryEntity, str] = {
    "phenopacket": DATA_TYPE_PHENOPACKET,
    "individual": DATA_TYPE_PHENOPACKET,
    "biosample": DATA_TYPE_PHENOPACKET,
    "experiment": DATA_TYPE_EXPERIMENT,
}
