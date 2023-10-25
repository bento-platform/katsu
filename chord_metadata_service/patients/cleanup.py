import chord_metadata_service.phenopackets.models as pm

from chord_metadata_service.cleanup.remove import remove_not_referenced
from chord_metadata_service.utils import build_id_set_from_model
from .models import Individual

__all__ = [
    "clean_individuals",
]


async def clean_individuals() -> int:
    """
    Deletes all individuals which aren't referenced anywhere in the application.
    Phenopackets/biosamples should be cleaned BEFORE running this.
    """

    individuals_referenced = set()

    # Collect references to individuals from Phenopackets
    individuals_referenced |= await build_id_set_from_model(pm.Biosample, "individual_id")
    individuals_referenced |= await build_id_set_from_model(pm.Phenopacket, "subject_id")

    # Remove individuals not collected above
    return await remove_not_referenced(Individual, individuals_referenced, "individuals")
