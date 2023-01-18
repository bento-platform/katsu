import chord_metadata_service.mcode.models as mm
import chord_metadata_service.phenopackets.models as pm

from chord_metadata_service.logger import logger
from chord_metadata_service.utils import dict_first_val
from .models import Individual


def clean_individuals() -> int:
    """
    Deletes all individuals which aren't referenced anywhere in the application.
    Phenopackets/biosamples should be cleaned BEFORE running this.
    """

    individuals_referenced = set()

    # Collect references to individuals from MCode
    individuals_referenced.update(map(dict_first_val, mm.LabsVital.objects.values("individual_id")))
    individuals_referenced.update(map(dict_first_val, mm.MCodePacket.objects.values("subject_id")))

    # Collect references to individuals from Phenopackets
    individuals_referenced.update(map(dict_first_val, pm.Biosample.objects.values("individual_id")))
    individuals_referenced.update(map(dict_first_val, pm.Phenopacket.objects.values("subject_id")))

    # Remove null from set
    individuals_referenced.discard(None)

    # Remove individuals NOT in set

    individuals_to_remove = set(
        map(dict_first_val, Individual.objects.exclude(id__in=individuals_referenced).values_list("id")))
    n_to_remove = len(individuals_to_remove)

    if n_to_remove:
        logger.info(f"Automatically cleaning up {n_to_remove} individuals: {str(individuals_to_remove)}")
        Individual.objects.filter(id__in=individuals_to_remove)
    else:
        logger.info("No individuals set for auto-removal")

    return n_to_remove
