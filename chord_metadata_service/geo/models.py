from django.contrib.gis.db import models
from django.contrib.gis.geos import Point

from chord_metadata_service.discovery.full_text_search import ToFTSReprMixin
from chord_metadata_service.restapi.models import BaseTimeStamp
from chord_metadata_service.restapi.validators import base_extra_properties_validator

from . import descriptions as d
from .constants import ISO_3166_1_ALPHA_3_COUNTRY_CODE_CHOICES

__all__ = [
    "GeoLocation",
]


class GeoLocation(BaseTimeStamp, ToFTSReprMixin):
    """
    Model describing a specific geographical location. Heavily inspired by the Progenetix GeoLocation schema block:
    https://schemablocks.org/schema_pages/Progenetix/GeoLocation/
    """

    # geometry:
    #  - serializes into a GeoJSON geometry object when rendering any instances as JSON
    point = models.PointField(
        spatial_index=True, help_text="Point (coordinates) specifying a precise geographic location."
    )

    # metadata / free-text data:
    #  - serializes into a GeoJSON properties object when rendering any instances as JSON
    label = models.TextField(blank=True, default="", help_text=d.PROP_LABEL)
    city = models.TextField(blank=True, default="", help_text=d.PROP_CITY)
    country = models.TextField(blank=True, default="", help_text=d.PROP_COUNTRY)
    iso_a3_code = models.CharField(
        max_length=3,
        choices=ISO_3166_1_ALPHA_3_COUNTRY_CODE_CHOICES,
        null=True,
        default=None,
        help_text=d.PROP_ISO3166_ALPHA_3,
    )
    precision = models.TextField(blank=True, default="", help_text=d.PROP_PRECISION)

    # properties (mapping to other properties in the GeoJSON object) which do not map to any of the above fields:
    extra_properties = models.JSONField(
        blank=True,
        default=dict,
        validators=[base_extra_properties_validator],
        help_text="Extra properties that do not have a predefined field in the database.",
    )

    # ------------------------------------------------------------------------------------------------------------------

    def fts_repr_values(self) -> tuple:
        return self.label, self.city, self.country, self.iso_a3_code, self.precision, self.extra_properties

    def __str__(self):
        # noinspection PyTypeChecker
        pt: Point = self.point
        return f"{self.label} {pt.coords}" if self.label else str(pt.coords)
