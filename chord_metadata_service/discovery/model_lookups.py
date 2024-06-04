from django.db.models import Model
from typing import Literal, Type, TypedDict

from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.experiments import models as exp_models
from chord_metadata_service.patients import models as patient_models
from chord_metadata_service.phenopackets import models as pheno_models

__all__ = ["PUBLIC_MODEL_NAMES_TO_MODEL", "PUBLIC_MODEL_NAMES_TO_DATA_TYPE"]

PublicModelNames = Literal["individual", "biosample", "experiment"]

PUBLIC_MODEL_NAMES_TO_MODEL: dict[PublicModelNames, Type[Model]] = {
    "individual": patient_models.Individual,
    "biosample": pheno_models.Biosample,
    "experiment": exp_models.Experiment,
}

PUBLIC_MODEL_NAMES_TO_DATA_TYPE: dict[PublicModelNames, str] = {
    "individual": DATA_TYPE_PHENOPACKET,
    "biosample": DATA_TYPE_PHENOPACKET,
    "experiment": DATA_TYPE_EXPERIMENT,
}


class ScopeFilter(TypedDict):
    filter: str
    prefetch_related: tuple[str]
    select_related: tuple[str]


class ProjectDatasetScopeFilters(TypedDict):
    project: ScopeFilter
    dataset: ScopeFilter


PUBLIC_MODEL_NAMES_TO_SCOPE_FILTERS: dict[PublicModelNames, ProjectDatasetScopeFilters] = {
    "individual": {
        "project": {
            "filter": "phenopackets__dataset__project__identifier",
            "prefetch_related": ("phenopackets__dataset__project")
        },
        "dataset": {
            "filter": "phenopackets__dataset__identifier",
            "prefetch_related": ("phenopackets__dataset")
        },
    },
    "biosample": {
        "project": {
            "filter": "phenopacket__dataset__project__identifier",
            "prefetch_related": ("phenopacket__dataset__project"),
        },
        "dataset": {
            "filter": "phenopacket__dataset__identifier",
            "prefetch_related": ("phenopacket__dataset"),
        },
    },
    "experiment": {
        "project": {
            "filter": "dataset__project__identifier",
            "prefetch_related": ("dataset__project"),
        },
        "dataset": {
            "filter": "dataset__identifier",
            "prefetch_related": ("dataset"),
        },
    },
}
