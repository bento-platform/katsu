from django.conf import settings
from django.test import TestCase


class TestSettings(TestCase):
    """
    Test the Django settings for CANDIG authorization.
    """

    def test_katsu_authorization_settings_are_valid(self):
        """
        If KATSU_AUTHORIZATION is OPA, then the other OPA variables must be set.
        """
        error_msg_url = "CANDIG_OPA_URL is not set in settings"
        error_msg_secret = "CANDIG_OPA_SECRET is not set in settings"
        error_msg_key = "CANDIG_OPA_SITE_ADMIN_KEY is not set in settings"

        if settings.KATSU_AUTHORIZATION == "OPA":
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
        else:
            with self.assertRaisesMessage(
                AssertionError, "KATSU_AUTHORIZATION is not set to a valid value"
            ):
                raise AssertionError("KATSU_AUTHORIZATION is not set to a valid value")
