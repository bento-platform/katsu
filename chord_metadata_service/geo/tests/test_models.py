from chord_metadata_service.discovery.full_text_search import FTSHelpersMixin
from .constants import GeoLocationTestCase


class GeoLocationModelTest(GeoLocationTestCase):

    def test_geo_location_string_representation(self):
        self.assertEqual(str(self.loc_1), "Kingston (44.2380626, -76.512335)")
        self.assertEqual(str(self.loc_2), "Kingston (44.2380626, -76.512335)")
        self.assertEqual(str(self.loc_3), "(44.2380626, -76.512335)")

    def test_geo_location_fts_repr(self):
        self.assertEqual(FTSHelpersMixin.fts_repr_values_to_str(self.loc_1), "Kingston")
        self.assertEqual(
            FTSHelpersMixin.fts_repr_values_to_str(self.loc_2),
            "Kingston Kingston Canada CDN my_extra_property",  # numbers are skipped since they're context-less
        )
        self.assertEqual(FTSHelpersMixin.fts_repr_values_to_str(self.loc_3), "")
