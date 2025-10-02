"""
This file contains functions to build match response lists for the discovery matches endpoint.
These match lists are built from the match models in the pydantic_models.py file. They are not complete instances of
their corresponding entities, but rather are subsets right now.
Since we have pagination, though, we should probably fetch full record details in a future version - TODO
"""

from bento_lib.discovery import DiscoveryEntity
from django.db.models import Manager
from typing import Callable, TypeVar, TypedDict, Awaitable

from chord_metadata_service.authz.types import DataTypeDiscoveryPermissions
from chord_metadata_service.chord.data_types import DATA_TYPE_EXPERIMENT
from chord_metadata_service.experiments import models as em
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets import models as pm

from .pydantic_models import MatchBiosample, MatchExperiment, MatchExperimentResult, MatchPhenopacket, MatchIndividual
from .scope import ValidatedDiscoveryScope

__all__ = [
    "experiment_result_matches",
    "experiment_matches",
    "biosample_matches",
    "phenopacket_matches",
    "individual_matches",
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
    individual: str | None
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
                filename=er.filename,
                url=er.url,
                indices=er.indices,
                file_format=er.file_format,
                assembly_id=er.genome_assembly_id,
                **(
                    dict(
                        project=scope.project_id,
                        # TODO: have a foreign key to dataset directly to not have to do so many lookups (n+1 issue...)
                        dataset=scope.dataset_id or str((await er.experiments.afirst()).dataset_id),
                    )
                    if root else dict()
                ),
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
                study_type=exp.study_type,
                results=await experiment_result_matches(
                    exp.experiment_results, scope, dt_permissions, False, {**ctx, "experiment": str(exp.id)}
                ),
                **(dict(project=scope.project_id, dataset=scope.dataset_id or str(exp.dataset_id)) if root else dict()),
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
        p = (ctx or {}).get("phenopacket")
        ds = scope.dataset_id
        if not p and (p_obj := await b.phenopackets.afirst()):
            p = str(p_obj.id)
            ds = str(p_obj.dataset_id)

        res.append(
            MatchBiosample(
                id=str(b.id),
                phenopacket=p,
                experiments=(
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
                **(dict(project=scope.project_id, dataset=ds) if root else dict()),
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
                subject=s_id or None,
                biosamples=biosamples,
                **(
                    dict(
                        project=scope.project_id or (phe.dataset.project_id if phe.dataset else None),
                        dataset=scope.dataset_id or (str(phe.dataset_id) if phe.dataset else None),
                    ) if root else dict()
                ),
            )
        )

    return res


async def individual_matches(
    mrm: list[Individual] | Manager,
    scope: ValidatedDiscoveryScope,
    dt_permissions: DataTypeDiscoveryPermissions,
    root: bool,
    ctx: MatchContext,
) -> list[MatchIndividual]:
    res: list[MatchIndividual] = []

    for ind in await list_or_manager_to_list(mrm):
        ind_id = str(ind.id)
        # TODO: prefetch all the time, even when not filtering.
        # TODO: return both all phenopackets and matching phenopackets?
        phenopackets = await phenopacket_matches(
            getattr(ind, "phenopacket_matches", ind.phenopackets),
            scope,
            dt_permissions,
            False,
            {**ctx, "individual": ind_id},
        )

        first_phenopacket = await ind.phenopackets.prefetch_related("dataset").afirst()

        res.append(
            MatchIndividual(
                id=ind_id,
                phenopackets=phenopackets,
                **(
                    dict(
                        # TODO: put this on Individual itself, i.e., link individual with project/dataset?
                        project=scope.project_id or (
                            str(first_phenopacket.dataset.project_id) if first_phenopacket.dataset else None
                        ),
                        dataset=scope.dataset_id or str(first_phenopacket.dataset_id),
                    ) if root else dict()
                ),
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
    "individual": individual_matches,
    "biosample": biosample_matches,
    "experiment": experiment_matches,
    "experiment_result": experiment_result_matches,
}
