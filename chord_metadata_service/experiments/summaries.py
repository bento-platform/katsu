import asyncio

from django.db.models import QuerySet

from chord_metadata_service.restapi.censorship import thresholded_count
from chord_metadata_service.restapi.utils import queryset_stats_for_field
from . import models

__all__ = [
    "experiment_summary",
    "experiment_result_summary",
    "instrument_summary",
]


async def experiment_summary(experiments: QuerySet, low_counts_censored: bool) -> dict:
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
        queryset_stats_for_field(experiments, "study_type", low_counts_censored),
        queryset_stats_for_field(experiments, "experiment_type", low_counts_censored),
        queryset_stats_for_field(experiments, "molecule", low_counts_censored),
        queryset_stats_for_field(experiments, "library_strategy", low_counts_censored),
        queryset_stats_for_field(experiments, "library_source", low_counts_censored),
        queryset_stats_for_field(experiments, "library_selection", low_counts_censored),
        queryset_stats_for_field(experiments, "library_layout", low_counts_censored),
        queryset_stats_for_field(experiments, "extraction_protocol", low_counts_censored),
    )

    return {
        "count": thresholded_count(count, low_counts_censored),
        "study_type": study_type,
        "experiment_type": experiment_type,
        "molecule": molecule,
        "library_strategy": library_strategy,
        "library_source": library_source,
        "library_selection": library_selection,
        "library_layout": library_layout,
        "extraction_protocol": extraction_protocol,
    }


async def experiment_result_summary(experiments: QuerySet, low_counts_censored: bool) -> dict:
    experiment_results = models.ExperimentResult.objects.filter(
        experiment_set__id__in=experiments.values_list("id", flat=True))

    (
        count,
        file_format,
        data_output_type,
        usage,
    ) = await asyncio.gather(
        experiment_results.acount(),
        queryset_stats_for_field(experiment_results, "file_format", low_counts_censored),
        queryset_stats_for_field(experiment_results, "data_output_type", low_counts_censored),
        queryset_stats_for_field(experiment_results, "usage", low_counts_censored),
    )

    return {
        "count": thresholded_count(count, low_counts_censored),
        "file_format": file_format,
        "data_output_type": data_output_type,
        "usage": usage,
    }


async def instrument_summary(experiments: QuerySet, low_counts_censored: bool) -> dict:
    instruments = models.Instrument.objects.filter(experiment_set__id__in=experiments.values_list("id", flat=True))

    count, platform, model = await asyncio.gather(
        instruments.acount(),
        queryset_stats_for_field(instruments, "platform", low_counts_censored),
        queryset_stats_for_field(instruments, "model", low_counts_censored),
    )

    return {
        "count": thresholded_count(count, low_counts_censored),
        "platform": platform,
        "model": model,
    }
