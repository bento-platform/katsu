from django.test import TestCase

from ..ingest import get_or_create_geo_location
from .constants import KINGSTON_GEOM_JSON


class GeoLocationIngestTest(TestCase):
    def test_ingest_no_extra_props(self):
        gl1 = get_or_create_geo_location({"type": "Feature", "geometry": KINGSTON_GEOM_JSON})
        self.assertDictEqual(gl1.extra_properties, {})

        gl2 = get_or_create_geo_location(
            {
                "type": "Feature",
                "geometry": KINGSTON_GEOM_JSON,
                "properties": {
                    "label": "Kingston",
                    "country": "CAN",
                },
            }
        )
        self.assertEqual(gl2.label, "Kingston")
        self.assertEqual(gl2.country, "CAN")
        self.assertDictEqual(gl2.extra_properties, {})

    def test_ingest_extra_props(self):
        gl = get_or_create_geo_location(
            {
                "type": "Feature",
                "geometry": KINGSTON_GEOM_JSON,
                "properties": {
                    "label": "Kingston",
                    "country": "CAN",
                    "my_cool_prop": 4321,
                    "my_cool_prop_2": "abc",
                },
            }
        )

        self.assertEqual(gl.label, "Kingston")
        self.assertEqual(gl.country, "CAN")
        self.assertDictEqual(
            gl.extra_properties,
            {
                "my_cool_prop": 4321,
                "my_cool_prop_2": "abc",
            },
        )

    def test_ingest_no_props(self):
        gl = get_or_create_geo_location(
            {
                "type": "Feature",
                "geometry": KINGSTON_GEOM_JSON,
            }
        )

        self.assertEqual(gl.label, "")
        self.assertEqual(gl.country, "")
        self.assertDictEqual(gl.extra_properties, {})
