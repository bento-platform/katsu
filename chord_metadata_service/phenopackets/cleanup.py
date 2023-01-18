import chord_metadata_service.experiments.models as em
import chord_metadata_service.phenopackets.models as pm

from chord_metadata_service.logger import logger
from chord_metadata_service.utils import dict_first_val
from .models import Biosample


def clean_biosamples() -> int:
    """
    Deletes all biosamples which aren't referenced anywhere in the application.
    Phenopackets and Experiments model tables should be deleted in the database
    BEFORE running this.
    """

    biosamples_referenced = set()

    # Collect references to biosamples in other data types
    biosamples_referenced.update(map(dict_first_val, pm.Phenopacket.objects.values("biosamples__id")))
    biosamples_referenced.update(map(dict_first_val, em.Experiment.objects.values("biosample_id")))

    # Remove null from set
    biosamples_referenced.discard(None)

    # Remove individuals NOT in set
    biosamples_to_remove = set(
        map(dict_first_val, Biosample.objects.exclude(id__in=biosamples_referenced).values("id")))
    n_to_remove = len(biosamples_to_remove)

    if n_to_remove:
        logger.info(f"Automatically cleaning up {n_to_remove} biosamples: {str(biosamples_to_remove)}")
        Biosample.objects.filter(id__in=biosamples_to_remove).delete()
    else:
        logger.info("No biosamples set for auto-removal")

    return n_to_remove
