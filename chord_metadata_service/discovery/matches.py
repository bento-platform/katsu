from bento_lib.discovery import DiscoveryEntity
from django.db.models import Manager
from typing import Callable, TypeVar, TypedDict, Awaitable

from chord_metadata_service.authz.types import DataTypeDiscoveryPermissions
from chord_metadata_service.chord.data_types import DATA_TYPE_EXPERIMENT
from chord_metadata_service.experiments import models as em
from chord_metadata_service.phenopackets import models as pm

from .pydantic_models import MatchBiosample, MatchExperiment, MatchExperimentResult, MatchPhenopacket
from .scope import ValidatedDiscoveryScope

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


class MatchContext(TypedDict, total=False):
    phenopacket: str | None
    biosample: str | None
    experiment: str | None


async def experiment_result_matches(
    mrm,
    scope: ValidatedDiscoveryScope,
    _dt_permissions,
    root: bool,
    ctx: MatchContext,
) -> list[MatchExperimentResult]:
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
                **(dict(pr=scope.project_id, ds=scope.dataset_id) if root else dict()),
            )
        )
    return res


async def experiment_matches(
    mrm: list[em.Experiment] | Manager,
    scope: ValidatedDiscoveryScope,
    dt_permissions: DataTypeDiscoveryPermissions,
    root: bool,
    ctx: MatchContext,
) -> list[MatchExperiment]:
    res: list[MatchExperiment] = []
    for exp in await list_or_manager_to_list(mrm):
        # TODO: right now, experiment results are not filtered even if a query is executed on them.
        res.append(
            MatchExperiment(
                id=str(exp.id),
                r=await experiment_result_matches(
                    exp.experiment_results, scope, dt_permissions, False, {**ctx, "experiment": str(exp.id)}
                ),
                **(dict(pr=scope.project_id, ds=scope.dataset_id) if root else dict()),
            )
        )
    return res


async def biosample_matches(
    mrm: list[pm.Biosample] | Manager,
    scope: ValidatedDiscoveryScope,
    dt_permissions: DataTypeDiscoveryPermissions,
    root: bool,
    ctx: MatchContext,
) -> list[MatchBiosample]:
    res: list[MatchBiosample] = []
    for b in await list_or_manager_to_list(mrm):
        res.append(
            MatchBiosample(
                id=str(b.id),
                p=(ctx or {}).get("phenopacket"),
                e=(
                    # TODO: prefetch all the time, even when not filtering?
                    (
                        await experiment_matches(
                            getattr(b, "experiment_matches", b.experiments),
                            scope,
                            dt_permissions,
                            False,
                            {**ctx, "biosample": str(b.id)},
                        )
                    )
                    if dt_permissions[DATA_TYPE_EXPERIMENT].data else None
                ),
                **(dict(pr=scope.project_id, ds=scope.dataset_id) if root else dict()),
            )
        )
    return res


async def phenopacket_matches(
    mrm: list[pm.Phenopacket] | Manager,
    scope: ValidatedDiscoveryScope,
    dt_permissions: DataTypeDiscoveryPermissions,
    root: bool,
    ctx: MatchContext,
) -> list[MatchPhenopacket]:
    res: list[MatchPhenopacket] = []

    for phe in await list_or_manager_to_list(mrm):
        phe_id = str(phe.id)
        s_id = phe.subject_id
        # TODO: prefetch all the time, even when not filtering.
        # TODO: return both all biosamples and matching biosamples?
        biosamples = await biosample_matches(
            getattr(phe, "biosample_matches", phe.biosamples),
            scope,
            dt_permissions,
            False,
            {**ctx, "phenopacket": phe_id},
        )
        res.append(
            MatchPhenopacket(
                id=phe_id,
                s=s_id or None,
                b=biosamples,
                **(dict(pr=scope.project_id, ds=scope.dataset_id or str(phe.dataset_id)) if root else dict()),
            )
        )

    return res


DISCOVERY_ENTITY_TO_MATCH_FN: dict[
    DiscoveryEntity,
    Callable[
        [list | Manager, ValidatedDiscoveryScope, DataTypeDiscoveryPermissions, bool, MatchContext],
        Awaitable[list]
    ]
] = {
    "phenopacket": phenopacket_matches,
    "individual": phenopacket_matches,  # TODO
    "biosample": biosample_matches,
    "experiment": experiment_matches,
    "experiment_result": experiment_result_matches,
}
