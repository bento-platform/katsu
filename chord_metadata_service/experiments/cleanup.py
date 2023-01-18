# TODO

from chord_metadata_service.logger import logger
from chord_metadata_service.utils import dict_first_val
from .models import Experiment, ExperimentResult, Instrument

__all__ = [
    "clean_experiment_results",
    "clean_instruments",
]


# TODO: Remove this when we have one-to-many ?
def clean_experiment_results() -> int:
    results_referenced = set()

    # Collect references to results from experiments
    results_referenced.update(map(dict_first_val, Experiment.objects.values("experiment_results__id")))

    # Remove experiment results NOT in set
    results_to_remove = set(
        map(dict_first_val, ExperimentResult.objects.exclude(id__in=results_referenced).values_list("id")))
    n_to_remove = len(results_to_remove)

    if n_to_remove:
        logger.info(f"Automatically cleaning up {len(results_to_remove)} experiment results: {str(results_to_remove)}")
        ExperimentResult.objects.filter(id__in=results_to_remove).delete()
    else:
        logger.info("No experiment results set for auto-removal")

    return n_to_remove


def clean_instruments() -> int:
    instruments_referenced = set()

    # Collect references to results from experiments
    instruments_referenced.update(map(dict_first_val, Experiment.objects.values("instrument_id")))

    # Remove experiment results NOT in set
    instruments_to_remove = set(
        map(dict_first_val, Instrument.objects.exclude(id__in=instruments_referenced).values_list("id")))
    n_to_remove = len(instruments_to_remove)

    if instruments_to_remove:
        logger.info(f"Automatically cleaning up {len(instruments_to_remove)} instruments: {str(instruments_to_remove)}")
        Instrument.objects.filter(id__in=instruments_to_remove).delete()
    else:
        logger.info("No instruments set for auto-removal")

    return n_to_remove
