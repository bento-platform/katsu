import chord_metadata_service.chord.models as cm
import chord_metadata_service.phenopackets.models as pm
from chord_metadata_service.resources.models import Resource

from chord_metadata_service.logger import logger
from chord_metadata_service.utils import dict_first_val

__all__ = [
    "clean_resources",
]


def clean_resources() -> int:
    """
    Removes any resources not referenced by any datasets/phenopackets.
    """

    resources_referenced = set()

    resources_referenced.update(map(dict_first_val, cm.Dataset.objects.values("additional_resources__id")))
    resources_referenced.update(map(dict_first_val, pm.MetaData.objects.values("resources__id")))

    # Remove null from set
    resources_referenced.discard(None)

    # Remove resources NOT in set
    resources_to_remove = set(
        map(dict_first_val, Resource.objects.exclude(id__in=resources_referenced).values("id")))
    n_to_remove = len(resources_to_remove)

    if n_to_remove:
        logger.info(f"Automatically cleaning up {n_to_remove} resources: {str(resources_to_remove)}")
        Resource.objects.filter(id__in=resources_to_remove).delete()
    else:
        logger.info("No resources set for auto-removal")

    return n_to_remove
