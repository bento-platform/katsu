import factory
from django.conf import settings
from rest_framework import status

from chord_metadata_service.mohpackets.models import SampleRegistration
from chord_metadata_service.mohpackets.serializers import SampleRegistrationSerializer
from chord_metadata_service.mohpackets.tests.endpoints.base import BaseTestCase
from chord_metadata_service.mohpackets.tests.endpoints.factories import (
    SampleRegistrationFactory,
)


# INGEST API
# ----------
class SampleRegistrationTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.sample_registration_url = "/v2/ingest/sample_registrations/"

    def test_sample_registration_create_authorized(self):
        """
        Test that an admin user can create a sample registration and receive 201 Created response.

        Testing Strategy:
        - Build SampleRegistration data based on the existing donor_id
        - An authorized user (user_2) with admin permission.
        - User can perform a POST request for sample registration creation.
        """
        sample_registration_data = SampleRegistrationFactory.build_batch(
            submitter_specimen_id=factory.Iterator(self.specimens),
            size=2,
        )
        serialized_data = SampleRegistrationSerializer(
            sample_registration_data, many=True
        ).data
        response = self.client.post(
            self.sample_registration_url,
            data=serialized_data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_sample_registration_create_unauthorized(self):
        """
        Test that a non-admin user attempting to create a sample registration receives a 403 Forbidden response.

        Testing Strategy:
        - Build SampleRegistration data based on the existing donor_id
        - An unauthorized user (user_0) with no permission.
        - User cannot perform a POST request for sample registration creation.
        """
        sample_registration_data = SampleRegistrationFactory.build_batch(
            submitter_specimen_id=factory.Iterator(self.specimens),
            size=2,
        )
        serialized_data = SampleRegistrationSerializer(
            sample_registration_data, many=True
        ).data
        response = self.client.post(
            self.sample_registration_url,
            data=serialized_data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.user_0.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
