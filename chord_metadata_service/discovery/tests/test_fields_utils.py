from django.test import TestCase, TransactionTestCase
from django.db.models import Q
from django.db.models.base import ModelBase

from chord_metadata_service.discovery.tests.constants import DISCOVERY_CONFIG_TEST
from ..fields_utils import (
    get_jsonb_path_query,
    get_json_range_condition,
    get_model_and_field,
    labelled_range_generator,
    get_nested_json_condition
)


class TestModelField(TransactionTestCase):

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

    def setUp(self) -> None:
        self.measurement_tumour = {
            "assay": {
                "id": "NCIT:C200479",
                "label": "Tumour length"
            },
            "value": {
                "quantity": {
                    "unit": {
                        "id": "UO:0000016",
                        "label": "mm"
                    },
                    "value": 40.0
                }
            }
        }
        self.measurement_bmi = {
            "assay": {
                "id": "NCIT:C16358",
                "label": "Body Mass Index"
            },
            "value": {
                "quantity": {
                    "unit": {
                        "id": "UO:0000086",
                        "label": "kg/m^2"
                    },
                    "value": 30.5
                }
            }
        }

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
        field_props = DISCOVERY_CONFIG_TEST["fields"]["measurement_tumor_length"]

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

    def test_jsonb_path_query_empty(self):
        model, field = get_model_and_field("biosample/measurements")
        assay_ids_query = get_jsonb_path_query(field, "assay/id")

        # no values
        assay_ids = model.objects.values_list(assay_ids_query)
        self.assertEqual(assay_ids.count(), 0)

    def test_jsonb_path_query_data(self):
        model, field = get_model_and_field("biosample/measurements")
        assay_ids_query = get_jsonb_path_query(field, "assay/id")

        # create a biosample with 2 types of measurements
        model.objects.create(
            id="0",
            measurements=[self.measurement_tumour, self.measurement_bmi]
        )

        # Get all measurement assay IDs
        assay_ids = model.objects.values_list(assay_ids_query)
        self.assertEqual(len(assay_ids), 2)

        # Get measurements values
        bmi_values_query = get_jsonb_path_query(field, "value/quantity/value")
        bmi_values = model.objects.values_list(bmi_values_query, flat=True)
        self.assertEqual(len(bmi_values), 2)
        self.assertEqual(bmi_values[0], self.measurement_tumour["value"]["quantity"]["value"])
        self.assertEqual(bmi_values[1], self.measurement_bmi["value"]["quantity"]["value"])
