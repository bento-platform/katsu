from unittest import TestCase
from ..fields_utils import labelled_range_generator


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
