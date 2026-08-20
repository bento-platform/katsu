from ..serializers import GeoLocationSerializer
from .constants import KINGSTON_GEOM_JSON, GeoLocationTestCase

VALID_GEO_LOCATION_PROPERTIES = (
    {},
    {"label": "my location"},
    {
        "country": "Canada",
        "ISO3166alpha3": "CDN",
        "my_cool_extra_prop": 5324,
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
        "geometry": KINGSTON_GEOM_JSON,
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
    },
)


class GeoLocationSerializersTest(GeoLocationTestCase):
    def test_valid_geo_location_no_props(self):
        GeoLocationSerializer(
            data={
                "type": "Feature",
                "geometry": KINGSTON_GEOM_JSON,
            }
        ).is_valid(raise_exception=True)

    def test_valid_geo_location(self):
        for props in VALID_GEO_LOCATION_PROPERTIES:
            with self.subTest(params=(props,)):
                GeoLocationSerializer(
                    data={
                        "type": "Feature",
                        "geometry": KINGSTON_GEOM_JSON,
                        "properties": props,
                    }
                ).is_valid(raise_exception=True)

    def test_valid_geo_location_with_altitude(self):
        for props in VALID_GEO_LOCATION_PROPERTIES:
            with self.subTest(params=(props,)):
                GeoLocationSerializer(
                    data={
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [44.2380626, -76.512335, 100.0],
                        },
                        "properties": props,
                    }
                ).is_valid(raise_exception=True)

    def test_invalid_geo_location(self):
        for loc in INVALID_GEO_LOCATIONS:
            with self.subTest(params=(loc,)):
                self.assertFalse(GeoLocationSerializer(data=loc).is_valid())

    def test_serialize_model_instance(self):
        for loc, loc_json in zip(
            self.locations,
            (
                {
                    "type": "Feature",
                    "geometry": KINGSTON_GEOM_JSON,
                    "properties": {"label": "Kingston"},
                },
                {
                    "type": "Feature",
                    "geometry": KINGSTON_GEOM_JSON,
                    "properties": {
                        "label": "Kingston",
                        "city": "Kingston",
                        "country": "Canada",
                        "ISO3166alpha3": "CDN",
                        # extra properties from model should be serialized into a flat representation in properties to
                        # be close to GeoJSON and support arbitrary GeoJSON consumers' demands for properties (e.g.,
                        # colour).
                        "my_extra_property": 4321,
                    },
                },
                {
                    "type": "Feature",
                    "geometry": KINGSTON_GEOM_JSON,
                    "properties": {},
                },
            ),
        ):
            with self.subTest(params=(loc, loc_json)):
                s = GeoLocationSerializer(instance=loc)
                self.assertDictEqual(s.data, loc_json)
