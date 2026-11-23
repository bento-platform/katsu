import structlog.stdlib
import sys
from bento_lib.discovery import DiscoveryConfig, DiscoveryConfigRules
from django.test import TestCase

from chord_metadata_service.authz.types import DataPermissions
from chord_metadata_service.authz.tests.helpers import PermissionsTestCaseMixin
from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.discovery.censorship import (
    censor_count,
    round_count,
    get_threshold,
    thresholded_count,
    get_max_query_parameters,
    censor_entity_counts,
    censor_entity_counts_by_dataset,
    aggregate_counts_from_censored_by_dataset,
)
from chord_metadata_service.discovery.types import EntityCountOrBoolResponse, EntityCounts
from .constants import DISCOVERY_CONFIG_TEST


test_logger = structlog.stdlib.get_logger("test_censorship")


class CensorshipGetThresholdTest(TestCase, PermissionsTestCaseMixin):
    # get_threshold(...)

    def test_get_threshold_no_censorship(self):
        self.assertEqual(get_threshold(DiscoveryConfig(), self.permissions_full), 0)

    def test_get_threshold_bool_only_perms(self):
        self.assertEqual(get_threshold(DiscoveryConfig(), self.permissions_bool), sys.maxsize)

        self.assertEqual(get_threshold(DISCOVERY_CONFIG_TEST, self.permissions_bool), 5)  # True threshold
        self.assertEqual(get_threshold(DISCOVERY_CONFIG_TEST.rules, self.permissions_bool), 5)  # same thing

    def test_get_threshold_empty_config(self):  # "empty" discovery config configured
        self.assertEqual(get_threshold(DiscoveryConfig(), self.permissions_counts), sys.maxsize)


class CensorshipThresholdedCountTest(TestCase, PermissionsTestCaseMixin):
    def test_get_threshold_configured(self):
        self.assertEqual(get_threshold(DISCOVERY_CONFIG_TEST, self.permissions_full), 0)
        self.assertEqual(get_threshold(DISCOVERY_CONFIG_TEST, self.permissions_counts), 5)

    # thresholded_count(...)

    def test_thresholded_count_no_censorship(self):
        self.assertEqual(thresholded_count(1, DiscoveryConfig(), self.permissions_full), 1)

    def test_thresholded_count_empty_config(self):
        self.assertEqual(thresholded_count(100000, DiscoveryConfig(), self.permissions_counts), 0)

    def test_thresholded_count_configured(self):
        self.assertEqual(thresholded_count(5, DISCOVERY_CONFIG_TEST, self.permissions_full), 5)
        self.assertEqual(thresholded_count(5, DISCOVERY_CONFIG_TEST.rules, self.permissions_full), 5)

        self.assertEqual(thresholded_count(5, DISCOVERY_CONFIG_TEST, self.permissions_counts), 0)
        self.assertEqual(thresholded_count(5, DISCOVERY_CONFIG_TEST.rules, self.permissions_counts), 0)


class CensorshipGetMaxQueryParametersTest(TestCase, PermissionsTestCaseMixin):
    # get_max_query_parameters(...)

    def test_get_max_query_parameters_no_censorship(self):
        self.assertEqual(get_max_query_parameters(DiscoveryConfig(), self.permissions_full), sys.maxsize)

    def test_get_max_query_parameters_empty_config(self):
        self.assertEqual(get_max_query_parameters(DiscoveryConfig(), self.permissions_counts), 0)

    def test_get_max_query_parameters_configured(self):
        self.assertEqual(get_max_query_parameters(DISCOVERY_CONFIG_TEST, self.permissions_full), sys.maxsize)
        self.assertEqual(get_max_query_parameters(DISCOVERY_CONFIG_TEST.rules, self.permissions_full), sys.maxsize)

        self.assertEqual(get_max_query_parameters(DISCOVERY_CONFIG_TEST, self.permissions_counts), 2)
        self.assertEqual(get_max_query_parameters(DISCOVERY_CONFIG_TEST.rules, self.permissions_counts), 2)


class CensorshipCensorEntityCountsTest(TestCase):
    # censor_entity_counts(...)

    LARGE_COUNTS: EntityCounts = {
        "phenopacket": 100,
        "individual": 100,
        "biosample": 100,
        "experiment": 100,
        "experiment_result": 100,
    }

    DT_PERMISSIONS_BOOL = {
        DATA_TYPE_PHENOPACKET: DataPermissions(bool_=True, counts=False, data=False),
        DATA_TYPE_EXPERIMENT: DataPermissions(bool_=True, counts=False, data=False),
    }

    DT_PERMISSIONS_COUNTS = {
        DATA_TYPE_PHENOPACKET: DataPermissions(bool_=True, counts=True, data=False),
        DATA_TYPE_EXPERIMENT: DataPermissions(bool_=True, counts=True, data=False),
    }

    DT_PERMISSIONS_PHE_COUNTS_EXP_BOOL = {
        DATA_TYPE_PHENOPACKET: DataPermissions(bool_=True, counts=True, data=False),
        DATA_TYPE_EXPERIMENT: DataPermissions(bool_=True, counts=False, data=False),
    }

    DT_PERMISSIONS_FULL = {
        DATA_TYPE_PHENOPACKET: DataPermissions(bool_=True, counts=True, data=True),
        DATA_TYPE_EXPERIMENT: DataPermissions(bool_=True, counts=True, data=True),
    }

    async def test_none(self):
        d = {**self.LARGE_COUNTS}
        await censor_entity_counts(DISCOVERY_CONFIG_TEST, d, self.DT_PERMISSIONS_COUNTS, test_logger)
        self.assertDictEqual(d, self.LARGE_COUNTS)

    async def test_experiments_experiment_results(self):
        d: EntityCounts = {**self.LARGE_COUNTS, "experiment": 0}
        r: EntityCountOrBoolResponse = await censor_entity_counts(
            DISCOVERY_CONFIG_TEST, d, self.DT_PERMISSIONS_COUNTS, test_logger
        )
        self.assertDictEqual(r, {**self.LARGE_COUNTS, "experiment": 0, "experiment_result": 0})

    async def test_experiments_experiment_results_bool(self):
        d: EntityCounts = {**self.LARGE_COUNTS, "experiment": 0}
        r: EntityCountOrBoolResponse = await censor_entity_counts(
            DISCOVERY_CONFIG_TEST, d, self.DT_PERMISSIONS_PHE_COUNTS_EXP_BOOL, test_logger
        )
        self.assertDictEqual(r, {**self.LARGE_COUNTS, "experiment": False, "experiment_result": False})

    async def test_experiments_experiment_results_full(self):
        d: EntityCounts = {**self.LARGE_COUNTS, "experiment": 0}
        # Full permissions, so no censorship should happen!
        r: EntityCountOrBoolResponse = await censor_entity_counts(
            DISCOVERY_CONFIG_TEST, d, self.DT_PERMISSIONS_FULL, test_logger
        )
        self.assertDictEqual(r, d)


class CensorshipCensorEntityCountsByDatasetTest(TestCase):
    COUNTS_BY_DATASET: dict[str, EntityCounts] = {
        "ds-1": {"phenopacket": 100, "individual": 100, "biosample": 100, "experiment": 100, "experiment_result": 100},
        "ds-2": {"phenopacket": 1, "individual": 1, "biosample": 0, "experiment": 0, "experiment_result": 0},
    }

    DT_PERMISSIONS_COUNTS = {
        DATA_TYPE_PHENOPACKET: DataPermissions(bool_=True, counts=True, data=False),
        DATA_TYPE_EXPERIMENT: DataPermissions(bool_=True, counts=True, data=False),
    }

    DT_PERMISSIONS_NONE = {
        DATA_TYPE_PHENOPACKET: DataPermissions(bool_=False, counts=False, data=False),
        DATA_TYPE_EXPERIMENT: DataPermissions(bool_=False, counts=False, data=False),
    }

    async def test_basic_censoring(self):
        result = await censor_entity_counts_by_dataset(
            DISCOVERY_CONFIG_TEST, self.COUNTS_BY_DATASET, self.DT_PERMISSIONS_COUNTS, test_logger
        )
        self.assertIn("ds-1", result)
        self.assertIn("ds-2", result)
        # ds-2 has phenopacket count of 1 which is below threshold of 5
        self.assertEqual(result["ds-2"]["phenopacket"], 0)

    async def test_no_permissions_excludes_dataset(self):
        # With no permissions, censor_entity_counts returns {}, so no datasets are added
        result = await censor_entity_counts_by_dataset(
            DISCOVERY_CONFIG_TEST, self.COUNTS_BY_DATASET, self.DT_PERMISSIONS_NONE, test_logger
        )
        self.assertDictEqual(result, {})


class CensorshipAggregateCountsFromCensoredByDatasetTest(TestCase):
    def test_aggregate_integers(self):
        counts_by_dataset: dict[str, EntityCountOrBoolResponse] = {
            "ds-1": {"phenopacket": 60, "individual": 60},
            "ds-2": {"phenopacket": 40, "individual": 40},
        }
        result = aggregate_counts_from_censored_by_dataset(counts_by_dataset)
        self.assertEqual(result["phenopacket"], 100)
        self.assertEqual(result["individual"], 100)

    def test_aggregate_booleans(self):
        # Boolean path: when dataset-level values are bools (bool-only permissions)
        counts_by_dataset: dict[str, EntityCountOrBoolResponse] = {
            "ds-1": {"phenopacket": True, "individual": True},
            "ds-2": {"phenopacket": False, "individual": False},
        }
        result = aggregate_counts_from_censored_by_dataset(counts_by_dataset)
        # OR across datasets: True | False = True
        self.assertIs(result["phenopacket"], True)
        self.assertIs(result["individual"], True)

    def test_aggregate_booleans_all_false(self):
        counts_by_dataset: dict[str, EntityCountOrBoolResponse] = {
            "ds-1": {"phenopacket": False},
        }
        result = aggregate_counts_from_censored_by_dataset(counts_by_dataset)
        self.assertIs(result["phenopacket"], False)


class CensorshipCountRoundingTest(TestCase):
    def test_round_count(self):
        self.assertEqual(round_count(37, 5), 35)
        self.assertEqual(round_count(38, 5), 40)
        self.assertEqual(round_count(40, 5), 40)
        self.assertEqual(round_count(37, 0), 37)  # no rounding

    def test_round_count_is_deterministic(self):
        self.assertEqual({round_count(37, 5) for _ in range(100)}, {35})

    def test_censor_count_no_rounding_matches_old_behaviour(self):
        self.assertEqual(censor_count(5, 5), 0)
        self.assertEqual(censor_count(6, 5), 6)
        self.assertEqual(censor_count(37, 5, 0), 37)

    def test_censor_count_with_rounding(self):
        # threshold 5, rounding 5: bins {A: 37, B: 3, missing: 0}, total 40
        total, a, b, missing = (censor_count(c, 5, 5) for c in (40, 37, 3, 0))
        self.assertEqual((total, a, b, missing), (40, 35, 0, 0))
        self.assertNotEqual(total - a, 3)  # the hidden bin B is not recoverable by subtraction

    def test_censor_count_never_rounds_above_threshold_down_to_zero(self):
        # threshold 1, rounding 10: 2 rounds to 0 under plain rounding, but must show as 10
        self.assertEqual(censor_count(2, 1, 10), 10)


class CensorshipRulesCountRoundingTest(TestCase, PermissionsTestCaseMixin):
    rules = DiscoveryConfigRules(count_threshold=5, max_query_parameters=2, count_rounding=5)

    def test_thresholded_count_rounds_with_counts_permission(self):
        counts_only = DataPermissions(counts=True)
        self.assertEqual([thresholded_count(c, self.rules, counts_only) for c in (3, 5, 37, 40)], [0, 0, 35, 40])

    def test_query_data_gets_exact_counts(self):
        self.assertEqual(thresholded_count(37, self.rules, DataPermissions(data=True)), 37)

    def test_censor_entity_counts_rounds(self):
        # sync check of the rule lookup used by censor_entity_counts
        from chord_metadata_service.discovery.censorship import get_count_rounding

        self.assertEqual(get_count_rounding(self.rules, DataPermissions(counts=True)), 5)
        self.assertEqual(get_count_rounding(self.rules, DataPermissions(data=True)), 0)
