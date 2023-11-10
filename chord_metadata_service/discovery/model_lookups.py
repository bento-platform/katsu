from django.db.models import Model
from typing import Type

from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.experiments import models as exp_models
from chord_metadata_service.patients import models as patient_models
from chord_metadata_service.phenopackets import models as pheno_models

__all__ = ["PUBLIC_MODEL_NAMES_TO_MODEL", "PUBLIC_MODEL_NAMES_TO_DATA_TYPE"]

PUBLIC_MODEL_NAMES_TO_MODEL: dict[str, Type[Model]] = {
    "individual": patient_models.Individual,
    "biosample": pheno_models.Biosample,
    "experiment": exp_models.Experiment,
}

PUBLIC_MODEL_NAMES_TO_DATA_TYPE = {
    "individual": DATA_TYPE_PHENOPACKET,
    "biosample": DATA_TYPE_PHENOPACKET,
    "experiment": DATA_TYPE_EXPERIMENT,
}
