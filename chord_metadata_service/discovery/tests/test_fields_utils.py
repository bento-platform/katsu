from bento_lib.discovery import NumberFieldDefinition
from chord_metadata_service.phenopackets.models import Biosample
from django.test import TestCase
from django.db.models import Q

from .constants import DISCOVERY_CONFIG_TEST
from ..fields_utils import (
    get_jsonb_path_query,
    get_json_range_condition,
    labelled_range_generator,
    get_nested_json_condition,
    str_to_numeric,
)


class TestLabelledRangeGenerator(TestCase):
    def setUp(self):
        self.fp: NumberFieldDefinition = NumberFieldDefinition.model_validate({
            "mapping": "individual/extra_properties/test",
            "datatype": "number",
            "title": "Test",
            "description": "A test field",
            "config": {
                "bin_size": 50,
                "taper_left": 50,
                "taper_right": 800,
                "minimum": 0,
                "maximum": 1000
            }
        })

    def test_config_with_tapers(self):
        rg = list(labelled_range_generator(self.fp))
        c = self.fp.config
        self.assertEqual(rg[0], (c.minimum, c.taper_left, f"< {c.taper_left}"))
        self.assertEqual(rg[-1], (c.taper_right, c.maximum, f"≥ {c.taper_right}"))
        self.assertEqual(
            rg[1],
            (c.taper_left, c.taper_left + c.bin_size, f"[{c.taper_left}, {c.taper_left + c.bin_size})"),
        )

    def test_config_without_tapers(self):
        self.fp.config.taper_left = 0
        self.fp.config.taper_right = 1000
        rg = list(labelled_range_generator(self.fp))
        self.assertIn("[", rg[0][2])
        self.assertIn("[", rg[-1][2])


class TestLabelledRangeGeneratorCustomBins(TestCase):
    def setUp(self):
        self.fp: NumberFieldDefinition = NumberFieldDefinition.model_validate({
            "mapping": "individual/extra_properties/test",
            "datatype": "number",
            "title": "Test",
            "description": "A test field",
            "config": {
                "bins": [5.5, 200, 300, 500, 1000, 1500, 2000],
                "minimum": 0,
                "units": "mg/L"
            }
        })

    def test_custom_bins_config(self):
        rg = list(labelled_range_generator(self.fp))
        self.assertEqual(rg[0], (0, 5.5, "< 5.5"))
        self.assertEqual(rg[-1], (2000, None, "≥ 2000"))
        self.assertEqual(rg[1], (5.5, 200, "[5.5, 200)"))

    def test_custom_bins_config_no_open_ended(self):
        self.fp.config.minimum = 0
        self.fp.config.bins.insert(0, 0)
        self.fp.config.maximum = 2000
        rg = list(labelled_range_generator(self.fp))
        self.assertIn("[", rg[0][2])
        self.assertIn("[", rg[-1][2])

    def test_str_to_numeric(self):
        subtests = [
            ("5.5", 5.5),
            ("5.", 5.0),
            ("5", 5),
            (".5", 0.5),
        ]

        for params in subtests:
            with self.subTest(params=params):
                self.assertEqual(str_to_numeric(params[0]), params[1])


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
        field_props = DISCOVERY_CONFIG_TEST.fields["measurement_tumor_length"]

        # GTE 0 an LT 20
        json_range_condition_0_20 = get_json_range_condition(
            "phenopacket", field_props, min_value=0, max_value=20
        )
        self.assertTrue(len(json_range_condition_0_20), 2)  # expect 2 conditions (GTE and LT)

        # GTE 0
        json_range_condition_gte_0 = get_json_range_condition("phenopacket", field_props, min_value=0)
        self.assertTrue(len(json_range_condition_gte_0), 1)

        # LT 20
        json_range_condition_lt_20 = get_json_range_condition("phenopacket", field_props, max_value=20)
        self.assertTrue(len(json_range_condition_lt_20), 1)

        # Combined Q object
        combined = Q()
        combined.add(json_range_condition_gte_0, Q.AND)
        combined.add(json_range_condition_lt_20, Q.AND)
        self.assertEqual(json_range_condition_0_20, combined)

        # GTE 0.5
        json_range_condition_gte_0_5 = get_json_range_condition("phenopacket", field_props, min_value=0.5)
        self.assertTrue(len(json_range_condition_gte_0_5), 1)

        # LT 20.5
        json_range_condition_lt_20_5 = get_json_range_condition("phenopacket", field_props, max_value=20.5)
        self.assertTrue(len(json_range_condition_lt_20_5), 1)

    def test_jsonb_path_query_empty(self):
        assay_ids_query = get_jsonb_path_query("measurements", "assay/id")

        # no values
        assay_ids = Biosample.objects.values_list(assay_ids_query)
        self.assertEqual(assay_ids.count(), 0)

    def test_jsonb_path_query_data(self):
        field = "measurements"
        assay_ids_query = get_jsonb_path_query(field, "assay/id")

        # create a biosample with 2 types of measurements
        Biosample.objects.create(
            id="0",
            measurements=[self.measurement_tumour, self.measurement_bmi]
        )

        # Get all measurement assay IDs
        assay_ids = Biosample.objects.values_list(assay_ids_query)
        self.assertEqual(len(assay_ids), 2)

        # Get measurements values
        bmi_values_query = get_jsonb_path_query(field, "value/quantity/value")
        bmi_values = Biosample.objects.values_list(bmi_values_query, flat=True)
        self.assertEqual(len(bmi_values), 2)
        self.assertEqual(bmi_values[0], self.measurement_tumour["value"]["quantity"]["value"])
        self.assertEqual(bmi_values[1], self.measurement_bmi["value"]["quantity"]["value"])
