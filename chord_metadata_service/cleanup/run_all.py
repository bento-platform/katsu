from structlog.stdlib import BoundLogger
from chord_metadata_service.experiments import cleanup as ec
from chord_metadata_service.geo import cleanup as gc
from chord_metadata_service.patients.cleanup import clean_individuals
from chord_metadata_service.phenopackets import cleanup as pc
from chord_metadata_service.resources.cleanup import clean_resources

__all__ = [
    "run_all_cleanup",
]


async def run_all_cleanup(logger: BoundLogger) -> int:
    # Specific order: biosamples, then experiment artifacts (results/instruments), then patients,
    # then resources (where order is less important)
    # TODO: figure out where order doesn't matter and use parallel asyncio.gather

    n_removed: int = 0

    # Phenopacket artifacts - metadata objects + biosamples + phenotypic features + interpretations + diagnoses
    #  + genomic/variant interpretations (order matters!)
    n_removed += await pc.clean_meta_data(logger)
    n_removed += await pc.clean_biosamples(logger)
    n_removed += await pc.clean_phenotypic_features(logger)
    n_removed += await pc.clean_interpretations(logger)
    n_removed += await pc.clean_diagnoses(logger)
    n_removed += await pc.clean_genomic_interpretations(logger)
    n_removed += await pc.clean_variant_interpretations(logger)

    # Geographic locations - referenced by biosamples (we first need to have cleaned biosamples above)
    n_removed += await gc.clean_geolocations(logger)

    # Experiment artifacts
    n_removed += await ec.clean_experiment_results(logger)
    n_removed += await ec.clean_instruments(logger)

    # Patients
    n_removed += await clean_individuals(logger)

    # Resources
    n_removed += await clean_resources(logger)

    # Return final removed object count
    return n_removed
