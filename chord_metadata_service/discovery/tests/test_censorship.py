import sys
from django.test import TestCase, override_settings

from chord_metadata_service.discovery.censorship import get_threshold, thresholded_count, get_max_query_parameters
from .constants import CONFIG_PUBLIC_TEST


class CensorshipGetThresholdTest(TestCase):

    # get_threshold(...)

    def test_get_threshold_no_censorship(self):
        self.assertEqual(get_threshold(low_counts_censored=False), 0)

    def test_get_threshold_no_config(self):  # no public config configured
        self.assertEqual(get_threshold(low_counts_censored=True), sys.maxsize)


class CensorshipThresholdedCountTest(TestCase):

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_get_threshold_configured(self):
        self.assertEqual(get_threshold(low_counts_censored=False), 0)
        self.assertEqual(get_threshold(low_counts_censored=True), 5)

    # thresholded_count(...)

    def test_thresholded_count_no_censorship(self):
        self.assertEqual(thresholded_count(1, low_counts_censored=False), 1)

    def test_thresholded_count_no_config(self):  # no public config configured
        self.assertEqual(thresholded_count(100000, low_counts_censored=True), 0)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_thresholded_count_configured(self):
        self.assertEqual(thresholded_count(5, low_counts_censored=False), 5)
        self.assertEqual(thresholded_count(5, low_counts_censored=True), 0)


class CensorshipGetMaxQueryParametersTest(TestCase):

    # get_max_query_parameters(...)

    def test_get_max_query_parameters_no_censorship(self):
        self.assertEqual(get_max_query_parameters(low_counts_censored=False), sys.maxsize)

    def test_get_max_query_parameters_no_config(self):
        self.assertEqual(get_max_query_parameters(low_counts_censored=True), 0)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_get_max_query_parameters_configured(self):
        self.assertEqual(get_max_query_parameters(low_counts_censored=False), sys.maxsize)
        self.assertEqual(get_max_query_parameters(low_counts_censored=True), 2)
