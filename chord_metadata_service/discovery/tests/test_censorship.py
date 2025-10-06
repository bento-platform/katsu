import structlog.stdlib
import sys
from bento_lib.discovery import DiscoveryConfig
from django.test import TestCase

from chord_metadata_service.authz.types import DataPermissions
from chord_metadata_service.authz.tests.helpers import PermissionsTestCaseMixin
from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.discovery.censorship import (
    get_threshold,
    thresholded_count,
    get_max_query_parameters,
    censor_entity_counts,
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
        "phenopacket": 100, "individual": 100, "biosample": 100, "experiment": 100, "experiment_result": 100
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
