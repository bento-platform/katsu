from django.test import TestCase

from ..serializers import GeoLocationPropertiesSerializer, GeoLocationSerializer

VALID_GEO_LOCATION_PROPERTIES = (
    {},
    {"label": "my location"},
    {
        "country": "Canada",
        "ISO3166alpha3": "CDN",
    },
    {
        "label": "David's Hometown",
        "city": "Kingston, ON",
        "country": "Canada",
        "ISO3166alpha3": "CDN",
        "precision": "city",
    },
)

INVALID_GEO_LOCATIONS = (
    {
        "type": "FeatureCollection",
        "geometry": {"type": "Point", "coordinates": [44.2380626, -76.512335]},
        "properties": {},
    },
    {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [44.2380626]},
        "properties": {},
    },
    {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [44.2380626, -76.512335, 44.2380626, -76.512335]},
        "properties": {},
    },
    {
        "type": "FeatureCollection",
        "geometry": {"type": "LineString", "coordinates": [[44.2380626, -76.512335], [44.2380626, -77.512335]]},
        "properties": {},
    }
)


class GeoLocationSerializersTest(TestCase):

    def test_valid_geo_location_properties(self):
        for props in VALID_GEO_LOCATION_PROPERTIES:
            with self.subTest(params=(props,)):
                self.assertTrue(GeoLocationPropertiesSerializer(data=props).is_valid())

    def test_valid_geo_location(self):
        for props in VALID_GEO_LOCATION_PROPERTIES:
            with self.subTest(params=(props,)):
                self.assertTrue(GeoLocationSerializer(data={
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [44.2380626, -76.512335],
                    },
                    "properties": props,
                }))

    def test_valid_geo_location_with_altitude(self):
        for props in VALID_GEO_LOCATION_PROPERTIES:
            with self.subTest(params=(props,)):
                self.assertTrue(GeoLocationSerializer(data={
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [44.2380626, -76.512335, 100.0],
                    },
                    "properties": props,
                }))

    def test_invalid_geo_location(self):
        for loc in INVALID_GEO_LOCATIONS:
            with self.subTest(params=(loc,)):
                self.assertFalse(GeoLocationSerializer(data=loc).is_valid())
