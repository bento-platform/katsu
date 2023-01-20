# TODO

from chord_metadata_service.cleanup.remove import remove_not_referenced
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
    return remove_not_referenced(ExperimentResult, results_referenced, "experiment results")


def clean_instruments() -> int:
    instruments_referenced = set()

    # Collect references to instruments from experiments
    instruments_referenced.update(map(dict_first_val, Experiment.objects.values("instrument_id")))

    # Remove instruments NOT in set
    return remove_not_referenced(Instrument, instruments_referenced, "instruments")
