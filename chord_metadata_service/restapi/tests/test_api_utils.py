from unittest import TestCase

from django.db.models.base import ModelBase
from django.test import override_settings
from rest_framework.test import APITestCase

from ..utils import (
    labelled_range_generator,
    get_model_and_field,
    get_date_stats,
    get_month_date_range)
from .constants import CONFIG_PUBLIC_TEST


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

    def test_config_with_tappers(self):
        rg = list(labelled_range_generator(self.fp))
        c = self.fp["config"]
        self.assertEqual(rg[0], (c["minimum"], c["taper_left"], f"< {c['taper_left']}"))
        self.assertEqual(rg[-1], (c["taper_right"], c["maximum"], f"≥ {c['taper_right']}"))
        self.assertEqual(rg[1], (c["taper_left"], c["taper_left"] + c["bin_size"],
                         f"{c['taper_left']}-{c['taper_left'] + c['bin_size']}"))

    def test_config_without_tappers(self):
        self.fp["config"] = {
            **self.fp["config"],
            "taper_left": 0,
            "taper_right": 1000
        }
        rg = list(labelled_range_generator(self.fp))
        self.assertIn("-", rg[0][2])
        self.assertIn("-", rg[-1][2])

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


class TestModelField(TestCase):

    def test_get_model_field_basic(self):
        model, field = get_model_and_field("individual/age_numeric")
        self.assertIsInstance(model, ModelBase)
        self.assertEqual(field, "age_numeric")

        model, field = get_model_and_field("experiment/experiment_type")
        self.assertIsInstance(model, ModelBase)
        self.assertEqual(field, "experiment_type")

    def test_get_model_nested_field(self):
        model, field = get_model_and_field("individual/extra_properties/lab_test_result")
        self.assertEqual(field, "extra_properties__lab_test_result")

    def test_get_wrong_model(self):
        self.assertRaises(NotImplementedError, get_model_and_field, "junk/age_numeric")


class TestDateStatsExcept(APITestCase):

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_wrong_bin_config(self):
        fp = {
            "mapping": "individual/extra_properties/date_of_consent",
            "datatype": "date",
            "config": {
                "bin_by": "year"
            }
        }
        self.assertRaises(NotImplementedError, get_date_stats, fp)
        self.assertRaises(NotImplementedError, get_month_date_range, fp)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_wrong_field_config(self):
        fp = {
            "mapping": "individual/date_of_consent",
            "datatype": "date",
            "config": {
                "bin_by": "month"
            }
        }
        self.assertRaises(NotImplementedError, get_date_stats, fp)
        self.assertRaises(NotImplementedError, get_month_date_range, fp)
