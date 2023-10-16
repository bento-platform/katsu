from chord_metadata_service.experiments import cleanup as ec
from chord_metadata_service.patients.cleanup import clean_individuals
from chord_metadata_service.phenopackets import cleanup as pc
from chord_metadata_service.resources.cleanup import clean_resources

__all__ = [
    "run_all_cleanup",
]


async def run_all_cleanup() -> int:
    # Specific order: biosamples, then experiment artifacts (results/instruments), then patients,
    # then resources (where order is less important)
    # TODO: figure out where order doesn't matter and use parallel asyncio.gather

    n_removed: int = 0

    # Phenopacket artifacts - metadata objects + biosamples + phenotypic features + procedures (order matters!)
    n_removed += await pc.clean_meta_data()
    n_removed += await pc.clean_biosamples()
    n_removed += await pc.clean_phenotypic_features()

    # Experiment artifacts
    n_removed += await ec.clean_experiment_results()
    n_removed += await ec.clean_instruments()

    # Patients
    n_removed += await clean_individuals()

    # Resources
    n_removed += await clean_resources()

    # Return final removed object count
    return n_removed
