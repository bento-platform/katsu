from django.db.models.base import ModelBase
from django.test import TransactionTestCase, override_settings
from rest_framework.test import APITestCase

from chord_metadata_service.patients import models as pa_m
from chord_metadata_service.phenopackets.tests import constants as ph_c

from .constants import CONFIG_PUBLIC_TEST
from ..fields_utils import get_model_and_field
from ..fields import (
    get_field_options,
    get_categorical_stats,
    get_date_stats,
    get_month_date_range,
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
