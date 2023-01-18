from chord_metadata_service.experiments.cleanup import clean_experiment_results, clean_instruments
from chord_metadata_service.patients.cleanup import clean_individuals
from chord_metadata_service.phenopackets.cleanup import clean_biosamples

__all__ = [
    "run_all_cleanup",
]


def run_all_cleanup() -> int:
    # Specific order: biosamples, then experiment artifacts (results/instruments), then patients

    n_removed: int = 0

    # Phenopacket artifacts - biosamples
    n_removed += clean_biosamples()

    # Experiment artifacts
    n_removed += clean_experiment_results()
    n_removed += clean_instruments()

    # Patients
    n_removed += clean_individuals()

    # Return final removed object count
    return n_removed
