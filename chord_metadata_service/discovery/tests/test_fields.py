from bento_lib.discovery import DiscoveryConfig
from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope
from django.test import TransactionTestCase, override_settings
from copy import deepcopy

from chord_metadata_service.authz.tests.helpers import PermissionsTestCaseMixin
from chord_metadata_service.chord.tests.helpers import ProjectTestCase
from chord_metadata_service.logger import logger
from chord_metadata_service.patients import models as pa_m
from chord_metadata_service.phenopackets.tests import constants as ph_c
from chord_metadata_service.phenopackets import models as ph_m

from .constants import DISCOVERY_CONFIG_TEST
from ..fields import get_field_options, get_categorical_stats, get_distinct_field_values, filter_queryset_field_value
from ..pydantic_models import BinWithValue


class TestGetFieldOptions(TransactionTestCase, PermissionsTestCaseMixin):
    discovery: DiscoveryConfig = DiscoveryConfig.model_validate({
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
    })

    async def test_get_string_options(self):
        test_scope = ValidatedDiscoveryScope(None, None)
        test_scope._discovery = TestGetFieldOptions.discovery
        self.assertListEqual(
            await get_field_options("phenopacket", "some_prop", test_scope, self.permissions_full),
            ["a", "b"]
        )

    async def test_get_field_options_not_impl(self):
        # {**self.field_some_prop, "datatype": "made_up"}
        invalid_discovery = deepcopy(self.discovery)
        invalid_discovery.fields["some_prop"].datatype = "made_up"

        test_scope = ValidatedDiscoveryScope(None, None)
        test_scope._discovery = invalid_discovery

        with self.assertRaises(NotImplementedError):
            # noinspection PyTypeChecker
            await get_field_options("phenopacket", "some_prop", test_scope, self.permissions_full)


class TestGetCategoricalStats(ProjectTestCase, PermissionsTestCaseMixin):

    def setUp(self):
        self.individual_1 = pa_m.Individual.objects.create(**ph_c.VALID_INDIVIDUAL_1)
        self.meta_data = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_1)
        self.phenopacket = ph_m.Phenopacket.objects.create(
            id="phenopacket_id:1",
            subject=self.individual_1,
            dataset=self.dataset,
            meta_data=self.meta_data,
        )

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    async def test_categorical_stats_lcf(self):
        res = await get_categorical_stats(
            self.scope,
            "phenopacket",
            ph_m.Phenopacket.objects.all(),
            DISCOVERY_CONFIG_TEST.fields["sex"],
            field_permissions=self.permissions_full,
        )
        self.assertListEqual(
            res.root, [BinWithValue(label="MALE", value=1), BinWithValue(label="missing", value=0)]
        )

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    async def test_categorical_stats_lct(self):
        res = await get_categorical_stats(
            self.scope,
            "phenopacket",
            ph_m.Phenopacket.objects.all(),
            DISCOVERY_CONFIG_TEST.fields["sex"],
            field_permissions=self.permissions_counts,
        )
        self.assertListEqual(res.root, [BinWithValue(label="missing", value=0)])


class TestJsonFieldArrayStats(ProjectTestCase, PermissionsTestCaseMixin):

    tumor_lengths = range(1, 50, 5)
    dm_fp = DISCOVERY_CONFIG_TEST.fields["diagnostic_markers"]
    mtl_fp = DISCOVERY_CONFIG_TEST.fields["measurement_tumor_length"]
    dob_fp = DISCOVERY_CONFIG_TEST.fields["date_of_birth"]

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
            self.scope,
            "phenopacket",
            ph_m.Phenopacket.objects.all(),
            self.dm_fp,
            field_permissions=self.permissions_full,
        )
        ground_truth = [
            BinWithValue(label="Genetic Testing", value=1),
            BinWithValue(label="Hematology Test", value=1),
            BinWithValue(label="missing", value=0),
        ]
        self.assertListEqual(res.root, ground_truth)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    async def test_json_categorical_stats_lct(self):
        res = await get_categorical_stats(
            self.scope,
            "phenopacket",
            ph_m.Phenopacket.objects.all(),
            self.dm_fp,
            field_permissions=self.permissions_counts,
        )
        ground_truth = [
            BinWithValue(label="missing", value=0),
        ]
        self.assertListEqual(res.root, ground_truth)

    async def test_filter_queryset_field_value_string(self):
        base_qs = ph_m.Individual.objects.all()

        subtest_params = [
            ("Hematology Test", 1),
            ("Genetic Testing", 1),
            ("VALUE NOT IN DB", 0),
        ]

        for params in subtest_params:
            with self.subTest(params=params):
                q_val, expected_count = params
                qs, queried_entity = await filter_queryset_field_value("individual", base_qs, self.dm_fp, q_val, logger)
                self.assertEqual(await qs.acount(), expected_count)
                self.assertEqual(queried_entity, "biosample")

    async def test_filter_queryset_field_value_number(self):
        base_qs = ph_m.Individual.objects.all()
        base_qs_pheno = ph_m.Phenopacket.objects.all()

        subtest_params = [
            # below: "canonical" filters as generated by the binning logic
            ("≥ 0", 1),
            ("≥ 60", 0),
            ("< 60", 1),
            ("< 0", 0),
            ("[30, 50)", 1),
            ("[100, 200)", 0),
            # below: arbitrary range queries, for users with full data-querying access
            ("> 0", 1),
            ("≥ 1", 1),
            ("< 1", 0),
            ("≤ 1", 1),
            ("[1, 2]", 1),
            ("(0, 1)", 0),
            ("(0, 1]", 1),
            # TODO: more
        ]

        for params in subtest_params:
            with self.subTest(params=params):
                q_val, expected_count = params
                qs, queried_entity = await filter_queryset_field_value(
                    "individual", base_qs, self.mtl_fp, q_val, logger
                )
                self.assertEqual(await qs.acount(), expected_count)
                self.assertEqual(queried_entity, "phenopacket")
                qs, queried_entity = await filter_queryset_field_value(
                    "phenopacket", base_qs_pheno, self.mtl_fp, q_val, logger
                )
                self.assertEqual(await qs.acount(), expected_count)
                self.assertEqual(queried_entity, "phenopacket")

    async def test_filter_queryset_field_value_date(self):
        base_qs = ph_m.Individual.objects.all()
        base_qs_pheno = ph_m.Phenopacket.objects.all()

        dob_subtest_params = [
            # below: "canonical" filters as generated by the binning logic
            ("1966-12", 0),
            ("1967-01", 1),
            ("1967-02", 0),
            ("2000-12", 0),
            # below: arbitrary range queries, for users with full data-querying access
            ("1997-01-01", 0),
            ("1967-01-01", 1),
            ("[1966-12-31, 1967-01-02)", 1),
            ("[1966-12-31, 1967-01-01]", 1),
            ("(1966-12-31, 1967-01-01]", 1),
            ("(1967-01-01, 1967-01-02]", 0),
            ("(1966-12-31, 1967-01-02)", 1),
            ("(1967-01-01, 1967-01-02)", 0),
            ("≥ 1967-01-01", 1),
            ("> 1967-01-01", 0),
            ("≥ 1967-01-02", 0),
            ("< 1967-01-02", 1),
            ("< 1967-01-01", 0),
            ("≤ 1967-01-01", 1),
        ]

        for params in dob_subtest_params:
            with self.subTest(params=params):
                q_val, expected_count = params
                qs, queried_entity = await filter_queryset_field_value(
                    "individual", base_qs, self.dob_fp, q_val, logger
                )
                self.assertEqual(await qs.acount(), expected_count)
                self.assertEqual(queried_entity, "individual")
                qs, queried_entity = await filter_queryset_field_value(
                    "phenopacket", base_qs_pheno, self.dob_fp, q_val, logger
                )
                self.assertEqual(await qs.acount(), expected_count)
                self.assertEqual(queried_entity, "individual")

    async def test_get_distinct_values(self):
        base_qs_pheno = ph_m.Phenopacket.objects.all()

        # "uncensored": 0-threshold
        dm_values = await get_distinct_field_values(
            "phenopacket",  base_qs_pheno, DISCOVERY_CONFIG_TEST.fields["diagnostic_markers"], 0
        )
        self.assertEqual(len(dm_values), 2)
        self.assertTrue("Genetic Testing" in dm_values)
        self.assertTrue("Hematology Test" in dm_values)

        # censored: 5-threshold eliminates all options
        dm_values_censored = await get_distinct_field_values(
            "phenopacket",  base_qs_pheno, DISCOVERY_CONFIG_TEST.fields["diagnostic_markers"], 5
        )
        self.assertListEqual(dm_values_censored, [])
