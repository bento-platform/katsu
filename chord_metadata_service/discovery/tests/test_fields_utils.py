from bento_lib.discovery import NumberFieldDefinition, DiscoveryEntity
from chord_metadata_service.phenopackets.models import Biosample
from django.test import TestCase, TransactionTestCase
from django.db.models import Q

from .constants import DISCOVERY_CONFIG_TEST, DISCOVERY_CONFIG_EXTRA_PROPERTIES
from ..exceptions import DiscoveryFilterRewriteException
from ..fields_utils import (
    get_jsonb_path_query,
    get_json_range_condition,
    get_field_django_mapping_and_queried_entity,
    get_field_django_mapping,
    labelled_range_generator,
    get_nested_json_condition,
    resolve_filter_mapping_to_queryset_model,
    normalize_field_path_true_model,
)


class TestModelField(TransactionTestCase):

    def test_get_model_field_basic(self):
        field, _, queried_entity = get_field_django_mapping_and_queried_entity(
            "phenopacket", DISCOVERY_CONFIG_TEST.fields["age"]
        )
        self.assertEqual(field, "subject__age_numeric")
        self.assertEqual(
            field, "subject__" + get_field_django_mapping("individual", DISCOVERY_CONFIG_TEST.fields["age"])
        )
        self.assertEqual(queried_entity, "individual")

        field = get_field_django_mapping("experiment", DISCOVERY_CONFIG_TEST.fields["extraction_protocol"])
        self.assertEqual(field, "extraction_protocol")

    def test_get_model_nested_field(self):
        field = get_field_django_mapping(
            "individual", DISCOVERY_CONFIG_EXTRA_PROPERTIES.fields["lab_test_result_value"]
        )
        self.assertEqual(field, "extra_properties__lab_test_result_value")

    def test_get_model_field_rewrite(self):
        field = get_field_django_mapping("phenopacket", DISCOVERY_CONFIG_TEST.fields["age"])
        self.assertEqual(field, "subject__age_numeric")

        # TODO

    def test_get_wrong_model(self):
        with self.assertRaises(DiscoveryFilterRewriteException):
            # noinspection PyTypeChecker
            get_field_django_mapping("junk", DISCOVERY_CONFIG_TEST.fields["age"])


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
                "bins": [200, 300, 500, 1000, 1500, 2000],
                "minimum": 0,
                "units": "mg/L"
            }
        })

    def test_custom_bins_config(self):
        rg = list(labelled_range_generator(self.fp))
        self.assertEqual(rg[0], (0, 200, "< 200"))
        self.assertEqual(rg[-1], (2000, None, "≥ 2000"))
        self.assertEqual(rg[1], (200, 300, "[200, 300)"))

    def test_custom_bins_config_no_open_ended(self):
        self.fp.config.minimum = 200
        self.fp.config.maximum = 2000
        rg = list(labelled_range_generator(self.fp))
        self.assertIn("[", rg[0][2])
        self.assertIn("[", rg[-1][2])


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
        json_range_condition_0_20 = get_json_range_condition("phenopacket", field_props, min=0, max=20)
        self.assertTrue(len(json_range_condition_0_20), 2)  # expect 2 conditions (GTE and LT)

        # GTE 0
        json_range_condition_gte_0 = get_json_range_condition("phenopacket", field_props, min=0)
        self.assertTrue(len(json_range_condition_gte_0), 1)

        # LT 20
        json_range_condition_lt_20 = get_json_range_condition("phenopacket", field_props, max=20)
        self.assertTrue(len(json_range_condition_lt_20), 1)

        # Combined Q object
        combined = Q()
        combined.add(json_range_condition_gte_0, Q.AND)
        combined.add(json_range_condition_lt_20, Q.AND)
        self.assertEqual(json_range_condition_0_20, combined)

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


class TestResolveFilterMapping(TestCase):
    def test_resolve_filter_mapping(self):
        subtests: list[tuple[DiscoveryEntity, DiscoveryEntity, tuple[str, ...], str]] = [
            ("phenopacket", "individual", ("sex",), "subject__sex"),
            ("individual", "phenopacket", ("subject", "sex"), "sex"),
            (
                "experiment",
                "phenopacket",
                ("biosamples", "experiment", "extra_properties", "prop"),
                "extra_properties__prop",
            ),
            (
                "experiment",
                "phenopacket",
                ("biosamples", "experiments", "extra_properties", "prop"),
                "extra_properties__prop",
            ),
            ("biosample", "individual", ("sex",), "phenopackets__subject__sex"),
            ("biosample", "phenopacket", ("biosamples", "sampled_tissue"), "sampled_tissue"),
            # TODO: more
        ]

        for params in subtests:
            with self.subTest(params=params):
                self.assertEqual(resolve_filter_mapping_to_queryset_model(*params[:3]), params[3])

    def test_resolve_filter_mapping_exc(self):
        # we cannot rewrite these as invalid discovery entities
        subtests: list[tuple[DiscoveryEntity, str, tuple[str, ...]]] = [
            ("biosample", "junk", ("sex",)),
            ("experiment", "junk", ("subject", "sex")),
        ]

        for params in subtests:
            with self.subTest(params=params):
                with self.assertRaises(DiscoveryFilterRewriteException):
                    resolve_filter_mapping_to_queryset_model(*params)

    def test_normalize_field_path(self):
        subtests: list[tuple[tuple[DiscoveryEntity, tuple[str, ...]], tuple[DiscoveryEntity, tuple[str, ...]]]] = [
            (
                ("individual", ("phenopackets", "biosamples", "extra_properties", "some_prop")),
                ("biosample", ("extra_properties", "some_prop")),
            ),
            (
                ("phenopacket", ("subject", "sex")),
                ("individual", ("sex",)),
            ),
            (
                ("phenopacket", ("biosamples", "experiments", "extra_properties", "some_prop")),
                ("experiment", ("extra_properties", "some_prop")),
            ),
            # TODO: more
        ]

        for params in subtests:
            with self.subTest(params=params):
                self.assertTupleEqual(normalize_field_path_true_model(*params[0]), params[1])
