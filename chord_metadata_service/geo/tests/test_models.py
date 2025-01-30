from .constants import GeoLocationTestCase


class GeoLocationModelTest(GeoLocationTestCase):

    def test_geo_location_string_representation(self):
        self.assertEqual(str(self.loc_1), "Kingston (44.2380626, -76.512335)")
        self.assertEqual(str(self.loc_2), "Kingston (44.2380626, -76.512335)")
        self.assertEqual(str(self.loc_3), "(44.2380626, -76.512335)")
