from chord_metadata_service.experiments.cleanup import clean_experiment_results, clean_instruments
from chord_metadata_service.patients.cleanup import clean_individuals
from chord_metadata_service.phenopackets.cleanup import clean_biosamples, clean_phenotypic_features, clean_procedures
from chord_metadata_service.resources.cleanup import clean_resources

__all__ = [
    "run_all_cleanup",
]


def run_all_cleanup() -> int:
    # Specific order: biosamples, then experiment artifacts (results/instruments), then patients,
    # then resources (where order is less important)

    n_removed: int = 0

    # Phenopacket artifacts - biosamples + phenotypic features + procedures (order matters!)
    n_removed += clean_biosamples()
    n_removed += clean_phenotypic_features()
    n_removed += clean_procedures()

    # Experiment artifacts
    n_removed += clean_experiment_results()
    n_removed += clean_instruments()

    # Patients
    n_removed += clean_individuals()

    # Resources
    n_removed += clean_resources()

    # Return final removed object count
    return n_removed
