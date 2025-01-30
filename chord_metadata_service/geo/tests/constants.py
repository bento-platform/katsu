from django.contrib.gis.geos import Point
from django.test import TestCase
from ..models import GeoLocation

__all__ = ["KINGSTON_GEOM_JSON", "GeoLocationTestCase"]

KINGSTON_GEOM_JSON = {
    "type": "Point",
    "coordinates": [44.2380626, -76.512335],
}


class GeoLocationTestCase(TestCase):

    def setUp(self):
        self.loc_1 = GeoLocation.objects.create(point=Point(44.2380626, -76.512335), label="Kingston")
        self.loc_2 = GeoLocation.objects.create(
            point=Point(44.2380626, -76.512335),
            label="Kingston",
            city="Kingston",
            country="Canada",
            iso_a3_code="CDN",
        )
        self.loc_3 = GeoLocation.objects.create(point=Point(44.2380626, -76.512335))

        self.locations = (self.loc_1, self.loc_2, self.loc_3)
