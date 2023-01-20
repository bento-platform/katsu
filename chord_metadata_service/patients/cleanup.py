import chord_metadata_service.mcode.models as mm
import chord_metadata_service.phenopackets.models as pm

from chord_metadata_service.cleanup.remove import remove_not_referenced
from chord_metadata_service.utils import dict_first_val
from .models import Individual

__all__ = [
    "clean_individuals",
]


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

    # Remove individuals not collected above
    return remove_not_referenced(Individual, individuals_referenced, "individuals")
