import asyncio

from django.db.models import QuerySet

from chord_metadata_service.restapi.utils import queryset_stats_for_field
from . import models

__all__ = [
    "experiment_summary",
    "experiment_result_summary",
    "instrument_summary",
]


async def experiment_summary(experiments: QuerySet) -> dict:
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
        queryset_stats_for_field(experiments, "study_type"),
        queryset_stats_for_field(experiments, "experiment_type"),
        queryset_stats_for_field(experiments, "molecule"),
        queryset_stats_for_field(experiments, "library_strategy"),
        queryset_stats_for_field(experiments, "library_source"),
        queryset_stats_for_field(experiments, "library_selection"),
        queryset_stats_for_field(experiments, "library_layout"),
        queryset_stats_for_field(experiments, "extraction_protocol"),
    )

    return {
        "count": count,
        "study_type": study_type,
        "experiment_type": experiment_type,
        "molecule": molecule,
        "library_strategy": library_strategy,
        "library_source": library_source,
        "library_selection": library_selection,
        "library_layout": library_layout,
        "extraction_protocol": extraction_protocol,
    }


async def experiment_result_summary(experiments: QuerySet) -> dict:
    experiment_results = models.ExperimentResult.objects.filter(
        experiment_set__id__in=experiments.values_list("id", flat=True))

    (
        count,
        file_format,
        data_output_type,
        usage,
    ) = await asyncio.gather(
        experiment_results.acount(),
        queryset_stats_for_field(experiment_results, "file_format"),
        queryset_stats_for_field(experiment_results, "data_output_type"),
        queryset_stats_for_field(experiment_results, "usage"),
    )

    return {
        "count": count,
        "file_format": file_format,
        "data_output_type": data_output_type,
        "usage": usage,
    }


async def instrument_summary(experiments: QuerySet) -> dict:
    instruments = models.Instrument.objects.filter(experiment_set__id__in=experiments.values_list("id", flat=True))

    count, platform, model = await asyncio.gather(
        instruments.acount(),
        queryset_stats_for_field(instruments, "platform"),
        queryset_stats_for_field(instruments, "model"),
    )

    return {
        "count": count,
        "platform": platform,
        "model": model,
    }
