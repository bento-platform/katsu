import asyncio

from django.db.models import QuerySet

from chord_metadata_service.discovery.censorship import thresholded_count
from chord_metadata_service.discovery.stats import queryset_stats_for_field
from chord_metadata_service.discovery.types import DiscoveryConfig
from . import models

__all__ = [
    "experiment_summary",
    "experiment_result_summary",
    "instrument_summary",
    "dt_experiment_summary",
]


async def experiment_summary(experiments: QuerySet, discovery: DiscoveryConfig, low_counts_censored: bool) -> dict:
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
        queryset_stats_for_field(experiments, "study_type", discovery, low_counts_censored),
        queryset_stats_for_field(experiments, "experiment_type", discovery, low_counts_censored),
        queryset_stats_for_field(experiments, "molecule", discovery, low_counts_censored),
        queryset_stats_for_field(experiments, "library_strategy", discovery, low_counts_censored),
        queryset_stats_for_field(experiments, "library_source", discovery, low_counts_censored),
        queryset_stats_for_field(experiments, "library_selection", discovery, low_counts_censored),
        queryset_stats_for_field(experiments, "library_layout", discovery, low_counts_censored),
        queryset_stats_for_field(experiments, "extraction_protocol", discovery, low_counts_censored),
    )

    return {
        "count": thresholded_count(count, discovery, low_counts_censored),
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
    low_counts_censored: bool
) -> dict:
    experiment_results = models.ExperimentResult.objects.filter(experiment__in=experiments)

    (
        count,
        file_format,
        data_output_type,
        usage,
    ) = await asyncio.gather(
        experiment_results.acount(),
        queryset_stats_for_field(experiment_results, "file_format", discovery, low_counts_censored),
        queryset_stats_for_field(experiment_results, "data_output_type", discovery, low_counts_censored),
        queryset_stats_for_field(experiment_results, "usage", discovery, low_counts_censored),
    )

    return {
        "count": thresholded_count(count, discovery, low_counts_censored),
        "file_format": file_format,
        "data_output_type": data_output_type,
        "usage": usage,
    }


async def instrument_summary(experiments: QuerySet, discovery: DiscoveryConfig, low_counts_censored: bool) -> dict:
    instruments = models.Instrument.objects.filter(experiment__in=experiments).distinct()

    count, platform, model = await asyncio.gather(
        instruments.acount(),
        queryset_stats_for_field(instruments, "platform", discovery, low_counts_censored),
        queryset_stats_for_field(instruments, "model", discovery, low_counts_censored),
    )

    return {
        "count": thresholded_count(count, discovery, low_counts_censored),
        "platform": platform,
        "model": model,
    }


async def dt_experiment_summary(experiments: QuerySet, discovery: DiscoveryConfig, low_counts_censored: bool) -> dict:
    # Parallel-gather all statistics we may need for this response
    (
        experiments_count,
        experiment_summary_val,
        exp_res_summary_val,
        instrument_summary_val,
    ) = await asyncio.gather(
        experiments.acount(),
        experiment_summary(experiments, discovery, low_counts_censored),
        experiment_result_summary(experiments, discovery, low_counts_censored),
        instrument_summary(experiments, discovery, low_counts_censored),
    )

    return {
        "count": thresholded_count(experiments_count, discovery, low_counts_censored),
        "data_type_specific": {
            "experiments": experiment_summary_val,
            "experiment_results": exp_res_summary_val,
            "instruments": instrument_summary_val,
        },
    }
