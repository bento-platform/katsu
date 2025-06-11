from django.db.models import Manager
from typing import TypeVar

from chord_metadata_service.authz.types import DataTypeDiscoveryPermissions
from chord_metadata_service.chord.data_types import DATA_TYPE_EXPERIMENT
from chord_metadata_service.experiments import models as em
from chord_metadata_service.phenopackets import models as pm

from .pydantic_models import DiscoveryMatches, MatchBiosample, MatchExperiment, MatchExperimentResult, MatchPhenopacket

__all__ = [
    "experiment_result_matches",
    "experiment_matches",
    "biosample_matches",
    "phenopacket_matches_obj",
]

T = TypeVar("T")


async def list_or_manager_to_list(x: list[T] | Manager) -> list[T]:
    """
    Given an object which is either a list of T or an instance of a T manager in an async Django DB context,
    return a list[T].
    """
    return x if isinstance(x, list) else [y async for y in x.all()]


async def experiment_result_matches(mrm) -> list[MatchExperimentResult]:
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


async def experiment_matches(mrm: list[em.Experiment] | Manager) -> list[MatchExperiment]:
    res: list[MatchExperiment] = []
    for exp in await list_or_manager_to_list(mrm):
        # TODO: right now, experiment results are not filtered even if a query is executed on them.
        res.append(MatchExperiment(id=str(exp.id), r=await experiment_result_matches(exp.experiment_results)))
    return res


async def biosample_matches(
    mrm: list[pm.Biosample] | Manager, dt_permissions: DataTypeDiscoveryPermissions
) -> list[MatchBiosample]:
    res: list[MatchBiosample] = []
    for b in await list_or_manager_to_list(mrm):
        res.append(
            MatchBiosample(
                id=str(b.id),
                e=(
                    # TODO: prefetch all the time, even when not filtering?
                    (await experiment_matches(getattr(b, "experiment_matches", b.experiments)))
                    if dt_permissions[DATA_TYPE_EXPERIMENT].data else None
                ),
            )
        )
    return res


async def phenopacket_matches_obj(page_list, dt_permissions: DataTypeDiscoveryPermissions) -> DiscoveryMatches:
    res: list[MatchPhenopacket] = [
        MatchPhenopacket(
            # TODO: prefetch all the time, even when not filtering.
            id=str(phe.id),
            s=str(phe.subject_id) if phe.subject_id else None,
            b=await biosample_matches(getattr(phe, "biosample_matches", phe.biosamples), dt_permissions),
        )
        async for phe in page_list
    ]
    return DiscoveryMatches(root=res)
