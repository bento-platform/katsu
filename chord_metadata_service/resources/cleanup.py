import chord_metadata_service.chord.models as cm
import chord_metadata_service.phenopackets.models as pm

from .models import Resource

from chord_metadata_service.cleanup.remove import remove_not_referenced
from chord_metadata_service.utils import build_id_set_from_model

__all__ = [
    "clean_resources",
]


async def clean_resources() -> int:
    """
    Removes any resources not referenced by any datasets/phenopackets.
    """

    resources_referenced = set()

    resources_referenced |= await build_id_set_from_model(cm.Dataset, "additional_resources__id")
    resources_referenced |= await build_id_set_from_model(pm.MetaData, "resources__id")

    return await remove_not_referenced(Resource, resources_referenced, "resources")
