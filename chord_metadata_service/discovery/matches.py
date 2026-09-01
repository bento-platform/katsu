"""
This file contains functions to build match response lists for the discovery matches endpoint.
These match lists are built from the match models in the pydantic_models.py file. They are not complete instances of
their corresponding entities, but rather are subsets right now.
Since we have pagination, though, we should probably fetch full record details in a future version - TODO
"""

from __future__ import annotations

from bento_lib.discovery import DiscoveryEntity
from bento_lib.ontologies.models import OntologyClass
from django.db.models import QuerySet, Manager
from pydantic import AnyUrl
from typing import Awaitable, Callable, Type, TypeVar, TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models.fields.related_descriptors import ManyRelatedManager, RelatedManager

from chord_metadata_service.authz.types import DataTypeDiscoveryPermissions
from chord_metadata_service.chord.data_types import DATA_TYPE_EXPERIMENT
from chord_metadata_service.experiments import models as em
from chord_metadata_service.restapi import api_renderers as apir

from .pydantic_models import (
    MatchBiosample,
    MatchExperiment,
    ExperimentResultIndices,
    MatchExperimentResult,
    MatchPhenopacket,
    MatchIndividual,
)
from .scope import ValidatedDiscoveryScope

__all__ = [
    "experiment_result_matches",
    "experiment_matches",
    "biosample_matches",
    "phenopacket_matches",
    "individual_matches",
    "DISCOVERY_ENTITY_TO_MATCH_FN",
    "DISCOVERY_ENTITY_TO_CSV_RENDERER",
    "DISCOVERY_ENTITY_TO_XLSX_RENDERER",
]

T = TypeVar("T")


async def queryset_or_related_manager_to_list(
    qs: QuerySet | ManyRelatedManager | RelatedManager,
    prefetch: tuple[str, ...] = (),
    select_related: tuple[str, ...] = (),
) -> list[T]:
    """
    Given an object which is either a QuerySet of T or an instance of a T manager in an async Django DB context,
    return a list[T].
    """

    if isinstance(qs, Manager):
        qs = qs.all()

    if prefetch:
        qs = qs.prefetch_related(*prefetch)

    if select_related:
        qs = qs.select_related(*select_related)

    return [y async for y in qs]


class MatchContext(TypedDict, total=False):
    individual: str | None
    phenopacket: str | None
    biosample: str | None
    experiment: str | None


async def experiment_result_matches(
    mrm: QuerySet,
    scope: ValidatedDiscoveryScope,
    _dt_permissions,
    root: bool,
    ctx: MatchContext,
) -> list[MatchExperimentResult]:
    res: list[MatchExperimentResult] = []
    er: em.ExperimentResult
    for er in await queryset_or_related_manager_to_list(
        mrm, prefetch=("experiments", "experiments__dataset", "experiments__biosample__phenopackets")
    ):
        # noinspection PyUnresolvedReferences
        first_exp = await (
            er.experiments.select_related("biosample", "dataset").prefetch_related("biosample__phenopackets").afirst()
        )
        # TODO: n+1?
        phenopacket = (await first_exp.biosample.phenopackets.afirst()) if first_exp and first_exp.biosample else None

        res.append(
            MatchExperimentResult(
                id=er.id,
                identifier=er.identifier,  # TODO: cleanup this across Katsu
                description=er.description or "",  # TODO: clean up null vs blank?
                filename=er.filename,
                url=er.url,
                indices=ExperimentResultIndices.model_validate(er.indices),
                storage_uri=AnyUrl(er.storage_uri) if er.storage_uri else None,
                storage_server=er.storage_server,
                genome_assembly_id=er.genome_assembly_id,
                file_format=er.file_format,
                data_output_type=er.data_output_type,
                usage=er.usage,
                creation_date=er.creation_date,
                created_by=er.created_by,
                extra_properties=er.extra_properties,
                # ------------------------------------------------------------------------------------------------------
                experiments=[v async for v in er.experiments.values_list("id", flat=True)],
                phenopacket=ctx.get("phenopacket") or (phenopacket.id if phenopacket else None),
                # ------------------------------------------------------------------------------------------------------
                **(
                    dict(
                        project=scope.project_id or (str(first_exp.dataset.project_id) if first_exp else None),
                        # TODO: have a foreign key to dataset directly to not have to do so many lookups
                        dataset=scope.dataset_id or (str(first_exp.dataset_id) if first_exp else None),
                    )
                    if root else dict()
                ),
            )
        )
    return res


async def experiment_matches(
    mrm: QuerySet,
    scope: ValidatedDiscoveryScope,
    dt_permissions: DataTypeDiscoveryPermissions,
    root: bool,
    ctx: MatchContext,
) -> list[MatchExperiment]:
    res: list[MatchExperiment] = []
    for exp in await queryset_or_related_manager_to_list(
        mrm, select_related=("biosample",), prefetch=("biosample__phenopackets",)
    ):
        # TODO: right now, experiment results are not filtered even if a query is executed on them.
        phenopacket = (await exp.biosample.phenopackets.afirst()) if exp.biosample else None  # TODO: n+1?
        experiment_results = await experiment_result_matches(
            exp.experiment_results,
            scope,
            dt_permissions,
            False,
            {**ctx, "phenopacket": phenopacket.id if phenopacket else None, "experiment": str(exp.id)},
        )
        experiment_results.sort(key=lambda er: er.id)
        res.append(
            MatchExperiment(
                id=str(exp.id),
                description=exp.description,
                experiment_type=exp.experiment_type,
                experiment_ontology=(
                    OntologyClass.model_validate(exp.experiment_ontology) if exp.experiment_ontology else None
                ),
                study_type=exp.study_type,
                molecule=exp.molecule,
                molecule_ontology=(
                    OntologyClass.model_validate(exp.molecule_ontology) if exp.molecule_ontology else None
                ),
                results=experiment_results,
                # ------------------------------------------------------------------------------------------------------
                biosample=str(exp.biosample.id) if exp.biosample else None,
                phenopacket=str(phenopacket.id) if phenopacket else None,
                # ------------------------------------------------------------------------------------------------------
                **(dict(
                    project=scope.project_id or str(exp.dataset.project_id),
                    dataset=scope.dataset_id or str(exp.dataset_id)
                ) if root else dict()),
            )
        )
    return res


async def biosample_matches(
    mrm: QuerySet,
    scope: ValidatedDiscoveryScope,
    dt_permissions: DataTypeDiscoveryPermissions,
    root: bool,
    ctx: MatchContext,
) -> list[MatchBiosample]:
    res: list[MatchBiosample] = []
    for b in await queryset_or_related_manager_to_list(mrm):
        p = (ctx or {}).get("phenopacket")
        ds = scope.dataset_id
        if not p and (p_obj := await b.phenopackets.afirst()):
            p = str(p_obj.id)
            ds = str(p_obj.dataset_id)

        # TODO: prefetch all the time, even when not filtering?
        experiments = (
            await experiment_matches(
                getattr(b, "experiment_matches", b.experiments),
                scope,
                dt_permissions,
                False,
                {**ctx, "biosample": str(b.id)},
            )
        ) if dt_permissions[DATA_TYPE_EXPERIMENT].data else None

        if experiments:
            experiments.sort(key=lambda e: e.id)

        res.append(
            MatchBiosample(
                id=str(b.id),
                individual_id=str(b.individual_id) if b.individual_id else None,
                phenopacket=p,
                experiments=experiments,
                **(dict(project=scope.project_id, dataset=ds) if root else dict()),
            )
        )
    return res


async def phenopacket_matches(
    mrm: QuerySet,
    scope: ValidatedDiscoveryScope,
    dt_permissions: DataTypeDiscoveryPermissions,
    root: bool,
    ctx: MatchContext,
) -> list[MatchPhenopacket]:
    res: list[MatchPhenopacket] = []

    for phe in await queryset_or_related_manager_to_list(mrm, select_related=("dataset",)):
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
        biosamples.sort(key=lambda b: b.id)

        res.append(
            MatchPhenopacket(
                id=phe_id,
                subject=s_id or None,
                biosamples=biosamples,
                **(
                    dict(
                        project=scope.project_id or (str(phe.dataset.project_id) if phe.dataset else None),
                        dataset=scope.dataset_id or (str(phe.dataset_id) if phe.dataset else None),
                    ) if root else dict()
                ),
            )
        )

    return res


async def individual_matches(
    mrm: QuerySet,
    scope: ValidatedDiscoveryScope,
    dt_permissions: DataTypeDiscoveryPermissions,
    root: bool,
    ctx: MatchContext,
) -> list[MatchIndividual]:
    res: list[MatchIndividual] = []

    for ind in await queryset_or_related_manager_to_list(mrm, prefetch=("phenopackets__dataset",)):
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

        first_phenopacket = await ind.phenopackets.get_queryset().select_related("dataset").afirst()

        res.append(
            MatchIndividual(
                id=ind_id,
                phenopackets=phenopackets,
                **(
                    dict(
                        # TODO: put this on Individual itself, i.e., link individual with project/dataset?
                        project=scope.project_id or (
                            str(first_phenopacket.dataset.project_id) if first_phenopacket.dataset_id else None
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
        [QuerySet, ValidatedDiscoveryScope, DataTypeDiscoveryPermissions, bool, MatchContext],
        Awaitable[list]
    ]
] = {
    "phenopacket": phenopacket_matches,
    "individual": individual_matches,
    "biosample": biosample_matches,
    "experiment": experiment_matches,
    "experiment_result": experiment_result_matches,
}


DISCOVERY_ENTITY_TO_CSV_RENDERER: dict[DiscoveryEntity, Type[apir.KatsuCSVRenderer]] = {
    "phenopacket": apir.PhenopacketCSVRenderer,
    "individual": apir.IndividualCSVRenderer,
    "biosample": apir.BiosamplesCSVRenderer,
    "experiment": apir.ExperimentCSVRenderer,
    "experiment_result": apir.ExperimentResultCSVRenderer,
}

DISCOVERY_ENTITY_TO_XLSX_RENDERER: dict[DiscoveryEntity, Type[apir.KatsuXLSXRenderer]] = {
    "phenopacket": apir.PhenopacketXLSXRenderer,
    "individual": apir.IndividualXLSXRenderer,
    "biosample": apir.BiosamplesXLSXRenderer,
    "experiment": apir.ExperimentXLSXRenderer,
    "experiment_result": apir.ExperimentResultXLSXRenderer,
}
