from django.contrib.gis.db import models as geo_models
from pycountry import countries


__all__ = [
    "GeoLocation",
]

# noinspection PyUnresolvedReferences
ISO_3166_1_ALPHA_3_COUNTRY_CODES = {c.alpha_3: c.name for c in list(countries)}


class GeoLocation(geo_models.Model):
    """
    Model describing a specific geographical location. Heavily inspired by the Progenetix GeoLocation schema block:
    https://schemablocks.org/schema_pages/Progenetix/GeoLocation/
    """

    # geometry:
    #  - serializes into a GeoJSON geometry object when rendering any instances as JSON
    point = geo_models.PointField()

    # metadata / free-text data:
    #  - serializes into a GeoJSON properties object when rendering any instances as JSON
    label = geo_models.TextField()
    city = geo_models.TextField()
    country = geo_models.TextField()
    iso_a3_code = geo_models.CharField(max_length=3, choices=ISO_3166_1_ALPHA_3_COUNTRY_CODES, null=True)
    precision = geo_models.TextField()

    # TODO: extra properties
