from chord_metadata_service.patients.cleanup import clean_individuals
from chord_metadata_service.phenopackets.cleanup import clean_biosamples

__all__ = [
    "run_all_cleanup",
]


def run_all_cleanup():
    # Specific order: biosamples, then experiment artifacts, then patients
    clean_biosamples()
    # TODO: experiment results
    clean_individuals()
