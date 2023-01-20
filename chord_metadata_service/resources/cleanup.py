import chord_metadata_service.chord.models as cm
import chord_metadata_service.phenopackets.models as pm

from .models import Resource

from chord_metadata_service.cleanup.remove import remove_not_referenced
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

    return remove_not_referenced(Resource, resources_referenced, "resources")
