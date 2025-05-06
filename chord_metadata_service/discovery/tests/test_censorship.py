import sys
from bento_lib.discovery import DiscoveryConfig
from django.test import TestCase

from chord_metadata_service.authz.tests.helpers import PermissionsTestCaseMixin
from chord_metadata_service.discovery.censorship import get_threshold, thresholded_count, get_max_query_parameters
from .constants import DISCOVERY_CONFIG_TEST


class CensorshipGetThresholdTest(TestCase, PermissionsTestCaseMixin):

    # get_threshold(...)

    def test_get_threshold_no_censorship(self):
        self.assertEqual(get_threshold(DiscoveryConfig(), self.permissions_full), 0)

    def test_get_threshold_bool_only_perms(self):
        self.assertEqual(get_threshold(DiscoveryConfig(), self.permissions_bool), sys.maxsize)
        self.assertEqual(get_threshold(DISCOVERY_CONFIG_TEST, self.permissions_bool), 5)  # True threshold

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
        self.assertEqual(thresholded_count(5, DISCOVERY_CONFIG_TEST, self.permissions_counts), 0)


class CensorshipGetMaxQueryParametersTest(TestCase, PermissionsTestCaseMixin):

    # get_max_query_parameters(...)

    def test_get_max_query_parameters_no_censorship(self):
        self.assertEqual(get_max_query_parameters(DiscoveryConfig(), self.permissions_full), sys.maxsize)

    def test_get_max_query_parameters_empty_config(self):
        self.assertEqual(get_max_query_parameters(DiscoveryConfig(), self.permissions_counts), 0)

    def test_get_max_query_parameters_configured(self):
        self.assertEqual(get_max_query_parameters(DISCOVERY_CONFIG_TEST, self.permissions_full), sys.maxsize)
        self.assertEqual(get_max_query_parameters(DISCOVERY_CONFIG_TEST, self.permissions_counts), 2)
