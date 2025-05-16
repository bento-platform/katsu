import asyncio

from bento_lib.discovery import DiscoveryConfig
from django.db.models import QuerySet

from chord_metadata_service.authz.types import DataPermissions
from chord_metadata_service.discovery.censorship import thresholded_count
from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope
from chord_metadata_service.discovery.stats import queryset_stats_for_field
from . import models

__all__ = [
    "experiment_summary",
    "experiment_result_summary",
    "instrument_summary",
    "dt_experiment_summary",
]


async def experiment_summary(
    experiments: QuerySet, discovery: DiscoveryConfig, experiment_permissions: DataPermissions
) -> dict:
    # TODO: limit to authorized field list if we're in censored discovery mode - based on discovery config

    (
        count,
        study_type,
        experiment_type,
        molecule,
        library_strategy,
        library_source,
        library_selection,
        library_layout,
        extraction_protocol,
    ) = await asyncio.gather(
        experiments.acount(),
        queryset_stats_for_field(experiments, "study_type", discovery, experiment_permissions),
        queryset_stats_for_field(experiments, "experiment_type", discovery, experiment_permissions),
        queryset_stats_for_field(experiments, "molecule", discovery, experiment_permissions),
        queryset_stats_for_field(experiments, "library_strategy", discovery, experiment_permissions),
        queryset_stats_for_field(experiments, "library_source", discovery, experiment_permissions),
        queryset_stats_for_field(experiments, "library_selection", discovery, experiment_permissions),
        queryset_stats_for_field(experiments, "library_layout", discovery, experiment_permissions),
        queryset_stats_for_field(experiments, "extraction_protocol", discovery, experiment_permissions),
    )

    return {
        "count": thresholded_count(count, discovery, experiment_permissions),
        "study_type": study_type,
        "experiment_type": experiment_type,
        "molecule": molecule,
        "library_strategy": library_strategy,
        "library_source": library_source,
        "library_selection": library_selection,
        "library_layout": library_layout,
        "extraction_protocol": extraction_protocol,
    }


async def experiment_result_summary(
    experiments: QuerySet,
    discovery: DiscoveryConfig,
    experiment_permissions: DataPermissions,
) -> dict:
    experiment_results = models.ExperimentResult.objects.filter(experiments__in=experiments)

    (
        count,
        file_format,
        data_output_type,
        usage,
    ) = await asyncio.gather(
        experiment_results.acount(),
        queryset_stats_for_field(experiment_results, "file_format", discovery, experiment_permissions),
        queryset_stats_for_field(experiment_results, "data_output_type", discovery, experiment_permissions),
        queryset_stats_for_field(experiment_results, "usage", discovery, experiment_permissions),
    )

    return {
        "count": thresholded_count(count, discovery, experiment_permissions),
        "file_format": file_format,
        "data_output_type": data_output_type,
        "usage": usage,
    }


async def instrument_summary(
    experiments: QuerySet, discovery: DiscoveryConfig, experiment_permissions: DataPermissions
) -> dict:
    instruments = models.Instrument.objects.filter(experiments__in=experiments).distinct()

    count, platform, model = await asyncio.gather(
        instruments.acount(),
        queryset_stats_for_field(instruments, "platform", discovery, experiment_permissions),
        queryset_stats_for_field(instruments, "model", discovery, experiment_permissions),
    )

    return {
        "count": thresholded_count(count, discovery, experiment_permissions),
        "platform": platform,
        "model": model,
    }


async def dt_experiment_summary(
    scope: ValidatedDiscoveryScope, experiment_permissions: DataPermissions, queryset: QuerySet | None = None
) -> dict:
    discovery = scope.discovery

    # Start with either all experiments or a subset specified by a parameter
    experiments = queryset if queryset is not None else models.Experiment.objects.all()

    # Apply scope to existing queryset to enforce it on the summarization
    if dataset_id := scope.dataset_id:
        experiments = experiments.filter(dataset_id=dataset_id)
    elif project_id := scope.project_id:
        # Project is set but dataset isn't
        experiments = experiments.select_related("dataset").filter(dataset__project_id=project_id)

    # Parallel-gather all statistics we may need for this response
    (
        experiments_count,
        experiment_summary_val,
        exp_res_summary_val,
        instrument_summary_val,
    ) = await asyncio.gather(
        experiments.acount(),
        experiment_summary(experiments, discovery, experiment_permissions),
        experiment_result_summary(experiments, discovery, experiment_permissions),
        instrument_summary(experiments, discovery, experiment_permissions),
    )

    return {
        "count": thresholded_count(experiments_count, discovery, experiment_permissions),
        "data_type_specific": {
            "experiments": experiment_summary_val,
            "experiment_results": exp_res_summary_val,
            "instruments": instrument_summary_val,
        },
    }
