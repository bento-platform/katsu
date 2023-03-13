import logging

from django.conf import settings
from django.test import TestCase

logger = logging.getLogger(__name__)


class SettingsTestCase(TestCase):
    """
    Test the Django settings for CANDIG authorization.
    """

    def test_opa_integration_settings(self):
        """
        Test that the OPA integration settings are valid.
        """
        error_msg_url = "CANDIG_OPA_URL is not set in settings"
        error_msg_secret = "CANDIG_OPA_SECRET is not set in settings"
        error_msg_key = "CANDIG_OPA_SITE_ADMIN_KEY is not set in settings"

        if settings.KATSU_AUTHORIZATION == "OPA":
            logger.info("KATSU_AUTHORIZATION is OPA, testing with docker env settings")
            self.assertNotEqual(
                settings.CANDIG_OPA_URL, "LOCAL_SETTING_NO_OPA_URL", error_msg_url
            )
            self.assertNotEqual(
                settings.CANDIG_OPA_SECRET,
                "LOCAL_SETTING_NO_OPA_SECRET",
                error_msg_secret,
            )
            self.assertNotEqual(
                settings.CANDIG_OPA_SITE_ADMIN_KEY,
                "LOCAL_SETTING_NO_SITE_ADMIN_KEY",
                error_msg_key,
            )
        elif settings.KATSU_AUTHORIZATION == "LOCAL_SETTING_NO_AUTH":
            logger.info("KATSU_AUTHORIZATION is LOCAL, testing with local settings")
            self.assertEqual(settings.CANDIG_OPA_URL, "LOCAL_SETTING_NO_OPA_URL")
            self.assertEqual(settings.CANDIG_OPA_SECRET, "LOCAL_SETTING_NO_OPA_SECRET")
            self.assertEqual(
                settings.CANDIG_OPA_SITE_ADMIN_KEY, "LOCAL_SETTING_NO_SITE_ADMIN_KEY"
            )
        else:
            logger.warning(
                "Invalid KATSU_AUTHORIZATION setting, skipping OPA settings test"
            )
            self.skipTest(
                "Skipping OPA settings test as KATSU_AUTHORIZATION is not set to a valid value"
            )
