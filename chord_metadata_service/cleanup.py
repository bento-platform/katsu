from chord_metadata_service.experiments.cleanup import clean_experiment_results, clean_instruments
from chord_metadata_service.patients.cleanup import clean_individuals
from chord_metadata_service.phenopackets.cleanup import clean_biosamples

__all__ = [
    "run_all_cleanup",
]


def run_all_cleanup():
    # Specific order: biosamples, then experiment artifacts (results/instruments), then patients

    # Phenopacket artifacts
    clean_biosamples()

    # Experiment artifacts
    clean_experiment_results()
    clean_instruments()

    # Patients
    clean_individuals()
