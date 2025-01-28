import chord_metadata_service.phenopackets.models as pm

from chord_metadata_service.cleanup.remove import remove_not_referenced
from chord_metadata_service.utils import build_id_set_from_model
from .models import GeoLocation

__all__ = [
    "clean_geolocations",
]


async def clean_geolocations() -> int:
    """
    Deletes all locations which aren't referenced anywhere in the application.
    Phenopackets/biosamples should be cleaned BEFORE running this.
    """

    locations_referenced = set()

    # Collect references to locations from biosamples
    locations_referenced |= await build_id_set_from_model(pm.Biosample, "location_id")

    # Remove individuals not collected above
    return await remove_not_referenced(GeoLocation, locations_referenced, "geolocations")
