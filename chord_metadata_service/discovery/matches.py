from bento_lib.discovery import DiscoveryEntity
from django.db.models import Manager
from typing import Callable, TypeVar

from chord_metadata_service.authz.types import DataTypeDiscoveryPermissions
from chord_metadata_service.chord.data_types import DATA_TYPE_EXPERIMENT
from chord_metadata_service.experiments import models as em
from chord_metadata_service.phenopackets import models as pm

from .pydantic_models import MatchBiosample, MatchExperiment, MatchExperimentResult, MatchPhenopacket

__all__ = [
    "experiment_result_matches",
    "experiment_matches",
    "biosample_matches",
    "phenopacket_matches",
    "DISCOVERY_ENTITY_TO_MATCH_FN",
]

T = TypeVar("T")


async def list_or_manager_to_list(x: list[T] | Manager) -> list[T]:
    """
    Given an object which is either a list of T or an instance of a T manager in an async Django DB context,
    return a list[T].
    """
    return x if isinstance(x, list) else [y async for y in x.all()]


async def experiment_result_matches(mrm, _dt_permissions) -> list[MatchExperimentResult]:
    res: list[MatchExperimentResult] = []
    er: em.ExperimentResult
    async for er in mrm.all():
        # noinspection PyUnresolvedReferences
        res.append(
            MatchExperimentResult(
                id=er.id,
                f=er.filename,
                url=er.url,
                idx=er.indices,
                ff=er.file_format,
                g=er.genome_assembly_id,
            )
        )
    return res


async def experiment_matches(
    mrm: list[em.Experiment] | Manager, dt_permissions: DataTypeDiscoveryPermissions
) -> list[MatchExperiment]:
    res: list[MatchExperiment] = []
    for exp in await list_or_manager_to_list(mrm):
        # TODO: right now, experiment results are not filtered even if a query is executed on them.
        res.append(
            MatchExperiment(id=str(exp.id), r=await experiment_result_matches(exp.experiment_results, dt_permissions))
        )
    return res


async def biosample_matches(
    mrm: list[pm.Biosample] | Manager, dt_permissions: DataTypeDiscoveryPermissions, /, phenopacket: str | None
) -> list[MatchBiosample]:
    res: list[MatchBiosample] = []
    for b in await list_or_manager_to_list(mrm):
        res.append(
            MatchBiosample(
                id=str(b.id),
                p=phenopacket,
                e=(
                    # TODO: prefetch all the time, even when not filtering?
                    (await experiment_matches(getattr(b, "experiment_matches", b.experiments), dt_permissions))
                    if dt_permissions[DATA_TYPE_EXPERIMENT].data else None
                ),
            )
        )
    return res


async def phenopacket_matches(
    mrm: list[pm.Phenopacket] | None, dt_permissions: DataTypeDiscoveryPermissions
) -> list[MatchPhenopacket]:
    res: list[MatchPhenopacket] = []

    for phe in await list_or_manager_to_list(mrm):
        phe_id = str(phe.id)
        s_id = phe.subject_id
        # TODO: prefetch all the time, even when not filtering.
        # TODO: return both all biosamples and matching biosamples?
        biosamples = await biosample_matches(
            getattr(phe, "biosample_matches", phe.biosamples), dt_permissions, phenopacket=phe_id
        )
        res.append(MatchPhenopacket(id=phe_id, s=s_id or None, b=biosamples))

    return res


DISCOVERY_ENTITY_TO_MATCH_FN: dict[DiscoveryEntity, Callable] = {
    "phenopacket": phenopacket_matches,
    "individual": None,  # TODO
    "biosample": biosample_matches,
    "experiment": experiment_matches,
    "experiment_result": experiment_result_matches,
}
