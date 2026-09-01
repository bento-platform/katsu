from bento_lib.discovery import DiscoveryConfig, StringFieldDefinition
from bento_lib.discovery.models.fields import StringFieldConfig
from django.test import TestCase

from chord_metadata_service.discovery.utils import empty_discovery
from .constants import DISCOVERY_CONFIG_TEST


class TestDiscoveryUtils(TestCase):
    def test_empty_discovery(self):
        subtests = [
            (None, True),
            (DiscoveryConfig(), True),
            (DiscoveryConfig(fields={}), True),
            (
                DiscoveryConfig(
                    fields={
                        "test": StringFieldDefinition(
                            datatype="string",
                            mapping="individual/test",
                            title="Test",
                            description="Test",
                            config=StringFieldConfig(enum=None),
                        )
                    }
                ),
                True,
            ),
            (DISCOVERY_CONFIG_TEST, False),
        ]

        for params in subtests:
            with self.subTest(params=params):
                self.assertEqual(empty_discovery(params[0]), params[1])
