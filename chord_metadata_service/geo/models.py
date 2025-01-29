from django.contrib.gis.db import models as geo_models
from django.contrib.gis.geos import Point

from .constants import ISO_3166_1_ALPHA_3_COUNTRY_CODE_CHOICES


__all__ = [
    "GeoLocation",
]


class GeoLocation(geo_models.Model):
    """
    Model describing a specific geographical location. Heavily inspired by the Progenetix GeoLocation schema block:
    https://schemablocks.org/schema_pages/Progenetix/GeoLocation/
    """

    # geometry:
    #  - serializes into a GeoJSON geometry object when rendering any instances as JSON
    point = geo_models.PointField(spatial_index=True)

    # metadata / free-text data:
    #  - serializes into a GeoJSON properties object when rendering any instances as JSON
    label = geo_models.TextField(blank=True)
    city = geo_models.TextField(blank=True)
    country = geo_models.TextField(blank=True)
    iso_a3_code = geo_models.CharField(
        max_length=3, choices=ISO_3166_1_ALPHA_3_COUNTRY_CODE_CHOICES, null=True, default=None
    )
    precision = geo_models.TextField(blank=True)

    # TODO: extra properties

    def __str__(self):
        # noinspection PyTypeChecker
        pt: Point = self.point
        return f"{self.label} {pt.coords}" if self.label else str(pt.coords)
