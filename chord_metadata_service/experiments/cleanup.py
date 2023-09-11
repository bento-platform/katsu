# TODO

from chord_metadata_service.cleanup.remove import remove_not_referenced
from chord_metadata_service.utils import build_id_set_from_model
from .models import Experiment, ExperimentResult, Instrument

__all__ = [
    "clean_experiment_results",
    "clean_instruments",
]


# TODO: Remove this when we have one-to-many ?
async def clean_experiment_results() -> int:
    results_referenced = set()

    # Collect references to results from experiments
    results_referenced |= await build_id_set_from_model(Experiment, "experiment_results__id")

    # Remove experiment results NOT in set
    return await remove_not_referenced(ExperimentResult, results_referenced, "experiment results")


async def clean_instruments() -> int:
    instruments_referenced = set()

    # Collect references to instruments from experiments
    instruments_referenced |= await build_id_set_from_model(Experiment, "instrument_id")

    # Remove instruments NOT in set
    return await remove_not_referenced(Instrument, instruments_referenced, "instruments")
