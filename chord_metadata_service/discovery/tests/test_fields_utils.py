from django.test import TestCase
from django.db.models import Q

from chord_metadata_service.discovery.tests.constants import CONFIG_PUBLIC_TEST
from ..fields_utils import (
    get_json_range_condition,
    labelled_range_generator,
    get_nested_json_condition
)


class TestLabelledRangeGenerator(TestCase):
    def setUp(self):
        self.fp = {
            "config": {
                "bin_size": 50,
                "taper_left": 50,
                "taper_right": 800,
                "minimum": 0,
                "maximum": 1000
            }
        }

    def test_config_with_tapers(self):
        rg = list(labelled_range_generator(self.fp))
        c = self.fp["config"]
        self.assertEqual(rg[0], (c["minimum"], c["taper_left"], f"< {c['taper_left']}"))
        self.assertEqual(rg[-1], (c["taper_right"], c["maximum"], f"≥ {c['taper_right']}"))
        self.assertEqual(rg[1], (c["taper_left"], c["taper_left"] + c["bin_size"],
                         f"[{c['taper_left']}, {c['taper_left'] + c['bin_size']})"))

    def test_config_without_tappers(self):
        self.fp["config"] = {
            **self.fp["config"],
            "taper_left": 0,
            "taper_right": 1000
        }
        rg = list(labelled_range_generator(self.fp))
        self.assertIn("[", rg[0][2])
        self.assertIn("[", rg[-1][2])

    def test_wrong_config_min_max(self):
        self.fp["config"] = {
            **self.fp["config"],
            "minimum": 6000
        }
        rg = labelled_range_generator(self.fp)
        self.assertRaises(ValueError, list, rg)

    def test_wrong_config_min_tapper_left(self):
        self.fp["config"] = {
            **self.fp["config"],
            "minimum": 60
        }
        rg = labelled_range_generator(self.fp)
        self.assertRaises(ValueError, list, rg)

    def test_wrong_config_bin_size(self):
        self.fp["config"] = {
            **self.fp["config"],
            "bin_size": 251
        }
        rg = labelled_range_generator(self.fp)
        self.assertRaises(ValueError, list, rg)


class TestLabelledRangeGeneratorCustomBins(TestCase):
    def setUp(self):
        self.fp = {
            "config": {
                "bins": [200, 300, 500, 1000, 1500, 2000],
                "minimum": 0,
                "units": "mg/L"
            }
        }

    def test_custom_bins_config(self):
        rg = list(labelled_range_generator(self.fp))
        self.assertEqual(rg[0], (0, 200, "< 200"))
        self.assertEqual(rg[-1], (2000, None, "≥ 2000"))
        self.assertEqual(rg[1], (200, 300, "[200, 300)"))

    def test_custom_bins_config_no_open_ended(self):
        c = {
            "config": {
                **self.fp["config"],
                "minimum": 200,
                "maximum": 2000
            }
        }
        rg = list(labelled_range_generator(c))
        self.assertIn("[", rg[0][2])
        self.assertIn("[", rg[-1][2])

    def test_custom_bins_wrong_min(self):
        c = {
            "config": {
                **self.fp["config"],
                "minimum": 300
            }
        }
        rg = labelled_range_generator(c)
        self.assertRaises(ValueError, list, rg)

    def test_custom_bins_wrong_max(self):
        c = {
            "config": {
                **self.fp["config"],
                "maximum": 300
            }
        }
        rg = labelled_range_generator(c)
        self.assertRaises(ValueError, list, rg)

    def test_custom_bins_wrong_max_2(self):
        c = {
            "config": {
                **self.fp["config"],
                "maximum": -10
            }
        }
        rg = labelled_range_generator(c)
        self.assertRaises(ValueError, list, rg)

    def test_custom_bins_wrong_bins(self):
        c = {
            "config": {
                **self.fp["config"],
                "bins": [200]
            }
        }
        rg = labelled_range_generator(c)
        self.assertRaises(ValueError, list, rg)


class TestJsonFieldUtils(TestCase):

    def test_get_nested_json_condition(self):
        path = "assay/label"
        value = "The assay label"

        nested_condition = get_nested_json_condition(path, value)
        self.assertEqual(nested_condition, {
            "assay": {
                "label": value
            }
        })

    def test_get_json_range_condition(self):
        field_props = CONFIG_PUBLIC_TEST["fields"]["measurement_tumor_length"]

        # GTE 0 an LT 20
        json_range_condition_0_20 = get_json_range_condition(field_props, min=0, max=20)
        self.assertTrue(len(json_range_condition_0_20), 2)  # expect 2 conditions (GTE and LT)

        # GTE 0
        json_range_condition_gte_0 = get_json_range_condition(field_props, min=0)
        self.assertTrue(len(json_range_condition_gte_0), 1)

        # LT 20
        json_range_condition_lt_20 = get_json_range_condition(field_props, max=20)
        self.assertTrue(len(json_range_condition_lt_20), 1)

        # Combined Q object
        combined = Q()
        combined.add(json_range_condition_gte_0, Q.AND)
        combined.add(json_range_condition_lt_20, Q.AND)
        self.assertEqual(json_range_condition_0_20, combined)
