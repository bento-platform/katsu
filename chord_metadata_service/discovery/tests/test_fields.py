from django.test import TransactionTestCase, override_settings
from rest_framework.test import APITestCase

from chord_metadata_service.patients import models as pa_m
from chord_metadata_service.phenopackets.tests import constants as ph_c
from chord_metadata_service.phenopackets import models as ph_m

from .constants import CONFIG_PUBLIC_TEST
from ..fields import (
    get_field_options,
    get_categorical_stats,
    get_distinct_field_values,
    get_date_stats,
    get_month_date_range,
    filter_queryset_field_value,
)


class TestGetFieldOptions(TransactionTestCase):

    field_some_prop = {
        "datatype": "string",
        "mapping": "individual/extra_properties/some_prop",
        "title": "Some Prop",
        "description": "Some property",
        "config": {
            "enum": ["a", "b"],
        },
    }

    async def test_get_string_options(self):
        self.assertListEqual(await get_field_options(self.field_some_prop, low_counts_censored=False), ["a", "b"])

    async def test_get_field_options_not_impl(self):
        with self.assertRaises(NotImplementedError):
            # noinspection PyTypeChecker
            await get_field_options({**self.field_some_prop, "datatype": "made_up"}, low_counts_censored=False)


class TestGetCategoricalStats(TransactionTestCase):

    f_sex = {
        "mapping": "individual/sex",
        "datatype": "string",
        "title": "Sex",
        "description": "Sex",
        "config": {
            "enum": None,
        },
    }

    def setUp(self):
        self.individual_1 = pa_m.Individual.objects.create(**ph_c.VALID_INDIVIDUAL_1)

    async def test_categorical_stats_lcf(self):
        res = await get_categorical_stats(self.f_sex, low_counts_censored=False)
        self.assertListEqual(res, [{"label": "MALE", "value": 1}, {"label": "missing", "value": 0}])

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    async def test_categorical_stats_lct(self):
        res = await get_categorical_stats(self.f_sex, low_counts_censored=True)
        self.assertListEqual(res, [{"label": "missing", "value": 0}])


class TestDateStatsExcept(APITestCase):

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
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
            await get_date_stats(fp)

        with self.assertRaises(NotImplementedError):
            await get_month_date_range(fp)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
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
            await get_date_stats(fp)

        with self.assertRaises(NotImplementedError):
            await get_month_date_range(fp)


class TestJsonFieldArrayStats(TransactionTestCase):

    tumor_lengths = range(1, 50, 5)
    dm_fp = CONFIG_PUBLIC_TEST["fields"]["diagnostic_markers"]
    mtl_fp = CONFIG_PUBLIC_TEST["fields"]["measurement_tumor_length"]

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
        )
        self.phenopacket.biosamples.set([self.biosample])

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    async def test_json_categorical_stats_lcf(self):
        res = await get_categorical_stats(self.dm_fp, low_counts_censored=False)
        ground_truth = [
            {"label": "Genetic Testing", "value": 1},
            {"label": "Hematology Test", "value": 1},
            {"label": "missing", "value": 0},
        ]
        self.assertListEqual(res, ground_truth)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    async def test_json_categorical_stats_lct(self):
        res = await get_categorical_stats(self.dm_fp, low_counts_censored=True)
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
        dm_values = await get_distinct_field_values(self.dm_fp, False)
        self.assertEqual(len(dm_values), 2)
        self.assertTrue("Genetic Testing" in dm_values)
        self.assertTrue("Hematology Test" in dm_values)

        dm_values_censored = await get_distinct_field_values(self.dm_fp, True)
        self.assertListEqual(dm_values_censored, [])
