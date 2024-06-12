from django.test import TransactionTestCase, override_settings
from rest_framework.test import APITestCase
from copy import deepcopy

from chord_metadata_service.chord.tests.helpers import ProjectTestCase
from chord_metadata_service.discovery.types import DiscoveryConfig
from chord_metadata_service.patients import models as pa_m
from chord_metadata_service.phenopackets.tests import constants as ph_c
from chord_metadata_service.phenopackets import models as ph_m

from .constants import DISCOVERY_CONFIG_TEST
from ..fields import (
    get_field_options,
    get_categorical_stats,
    get_distinct_field_values,
    get_date_stats,
    get_month_date_range,
    filter_queryset_field_value,
)


class TestGetFieldOptions(TransactionTestCase):
    discovery: DiscoveryConfig = {
        "fields": {
            "some_prop": {
                "datatype": "string",
                "mapping": "individual/extra_properties/some_prop",
                "title": "Some Prop",
                "description": "Some property",
                "config": {
                    "enum": ["a", "b"],
                },
            }
        }
    }

    async def test_get_string_options(self):
        self.assertListEqual(await get_field_options("some_prop", self.discovery, False), ["a", "b"])

    async def test_get_field_options_not_impl(self):
        # {**self.field_some_prop, "datatype": "made_up"}
        invalid_discovery = deepcopy(self.discovery)
        invalid_discovery["fields"]["some_prop"]["datatype"] = "made_up"
        with self.assertRaises(NotImplementedError):
            # noinspection PyTypeChecker
            await get_field_options("some_prop", invalid_discovery, low_counts_censored=False)


class TestGetCategoricalStats(ProjectTestCase):

    def setUp(self):
        self.individual_1 = pa_m.Individual.objects.create(**ph_c.VALID_INDIVIDUAL_1)
        self.meta_data = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_1)
        self.phenopacket = ph_m.Phenopacket.objects.create(
            id="phenopacket_id:1",
            subject=self.individual_1,
            dataset=self.dataset,
            meta_data=self.meta_data,
        )

    async def test_categorical_stats_lcf(self):
        res = await get_categorical_stats("sex", DISCOVERY_CONFIG_TEST, project_id=self.project.identifier,
                                          dataset_id=self.dataset.identifier, low_counts_censored=False)
        self.assertListEqual(res, [{"label": "MALE", "value": 1}, {"label": "missing", "value": 0}])

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    async def test_categorical_stats_lct(self):
        res = await get_categorical_stats("sex", DISCOVERY_CONFIG_TEST, project_id=self.project.identifier,
                                          dataset_id=self.dataset.identifier, low_counts_censored=True)
        self.assertListEqual(res, [{"label": "missing", "value": 0}])


class TestDateStatsExcept(APITestCase):

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    async def test_wrong_bin_config(self):
        fp = {
            "title": "Date of Consent",
            "description": "Date of consent for study",
            "mapping": "individual/extra_properties/date_of_consent",
            "datatype": "date",
            "config": {
                "bin_by": "year"
            }
        }

        with self.assertRaises(NotImplementedError):
            await get_date_stats("date_of_consent", DISCOVERY_CONFIG_TEST)

        with self.assertRaises(NotImplementedError):
            await get_month_date_range(fp)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    async def test_wrong_field_config(self):
        fp = {
            "title": "Date of Consent",
            "description": "Date of consent for study",
            "mapping": "individual/date_of_consent",
            "datatype": "date",
            "config": {
                "bin_by": "month"
            }
        }

        with self.assertRaises(NotImplementedError):
            await get_date_stats("date_of_consent", DISCOVERY_CONFIG_TEST)

        with self.assertRaises(NotImplementedError):
            await get_month_date_range(fp)


class TestJsonFieldArrayStats(ProjectTestCase):

    tumor_lengths = range(1, 50, 5)
    dm_fp = DISCOVERY_CONFIG_TEST["fields"]["diagnostic_markers"]
    mtl_fp = DISCOVERY_CONFIG_TEST["fields"]["measurement_tumor_length"]

    def setUp(self) -> None:
        self.tumors = [ph_c.valid_measurement_tumor_length(length) for length in self.tumor_lengths]
        self.individual = pa_m.Individual.objects.create(**ph_c.VALID_INDIVIDUAL_1)
        self.biosample = ph_m.Biosample.objects.create(**ph_c.valid_biosample_1(self.individual))
        self.meta_data = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_1)
        self.phenopacket = ph_m.Phenopacket.objects.create(
            id="phenopacket_id:1",
            subject=self.individual,
            measurements=self.tumors,
            meta_data=self.meta_data,
            dataset=self.dataset,
        )
        self.phenopacket.biosamples.set([self.biosample])

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    async def test_json_categorical_stats_lcf(self):
        res = await get_categorical_stats(
            "diagnostic_markers",
            DISCOVERY_CONFIG_TEST,
            project_id=self.project.identifier,
            dataset_id=self.dataset.identifier,
            low_counts_censored=False
        )
        ground_truth = [
            {"label": "Genetic Testing", "value": 1},
            {"label": "Hematology Test", "value": 1},
            {"label": "missing", "value": 0},
        ]
        self.assertListEqual(res, ground_truth)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    async def test_json_categorical_stats_lct(self):
        res = await get_categorical_stats(
            "diagnostic_markers",
            DISCOVERY_CONFIG_TEST,
            project_id=self.project.identifier,
            dataset_id=self.dataset.identifier,
            low_counts_censored=True
        )
        ground_truth = [
            {"label": "missing", "value": 0},
        ]
        self.assertListEqual(res, ground_truth)

    def test_filter_queryset_field_value_string(self):
        base_qs = ph_m.Individual.objects.all()
        qs = filter_queryset_field_value(base_qs, self.dm_fp, "Hematology Test")
        self.assertEqual(qs.count(), 1)
        qs = filter_queryset_field_value(base_qs, self.dm_fp, "Genetic Testing")
        self.assertEqual(qs.count(), 1)
        qs = filter_queryset_field_value(base_qs, self.dm_fp, "VALUE NOT IN DB")
        self.assertEqual(qs.count(), 0)

    def test_filter_queryset_field_value_number(self):
        base_qs = ph_m.Individual.objects.all()

        qs = filter_queryset_field_value(base_qs, self.mtl_fp, "≥ 0")
        self.assertEqual(qs.count(), 1)

        qs = filter_queryset_field_value(base_qs, self.mtl_fp, "≥ 60")
        self.assertEqual(qs.count(), 0)

        qs = filter_queryset_field_value(base_qs, self.mtl_fp, "< 60")
        self.assertEqual(qs.count(), 1)

        qs = filter_queryset_field_value(base_qs, self.mtl_fp, "< 0")
        self.assertEqual(qs.count(), 0)

        qs = filter_queryset_field_value(base_qs, self.mtl_fp, "[30, 50)")
        self.assertEqual(qs.count(), 1)

        qs = filter_queryset_field_value(base_qs, self.mtl_fp, "[100, 200)")
        self.assertEqual(qs.count(), 0)

    async def test_get_distinct_values(self):
        dm_values = await get_distinct_field_values("diagnostic_markers", DISCOVERY_CONFIG_TEST, False)
        self.assertEqual(len(dm_values), 2)
        self.assertTrue("Genetic Testing" in dm_values)
        self.assertTrue("Hematology Test" in dm_values)

        dm_values_censored = await get_distinct_field_values("diagnostic_markers", DISCOVERY_CONFIG_TEST, True)
        self.assertListEqual(dm_values_censored, [])
