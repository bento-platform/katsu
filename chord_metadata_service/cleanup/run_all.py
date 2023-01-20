from chord_metadata_service.experiments import cleanup as ec
from chord_metadata_service.patients.cleanup import clean_individuals
from chord_metadata_service.phenopackets import cleanup as pc
from chord_metadata_service.resources.cleanup import clean_resources

__all__ = [
    "run_all_cleanup",
]


def run_all_cleanup() -> int:
    # Specific order: biosamples, then experiment artifacts (results/instruments), then patients,
    # then resources (where order is less important)

    n_removed: int = 0

    # Phenopacket artifacts - metadata objects + biosamples + phenotypic features + procedures (order matters!)
    n_removed += pc.clean_meta_data()
    n_removed += pc.clean_biosamples()
    n_removed += pc.clean_phenotypic_features()
    n_removed += pc.clean_procedures()

    # Experiment artifacts
    n_removed += ec.clean_experiment_results()
    n_removed += ec.clean_instruments()

    # Patients
    n_removed += clean_individuals()

    # Resources
    n_removed += clean_resources()

    # Return final removed object count
    return n_removed
