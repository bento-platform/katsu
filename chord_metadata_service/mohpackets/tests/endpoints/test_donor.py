from django.conf import settings
from rest_framework import status

from chord_metadata_service.mohpackets.serializers import DonorSerializer
from chord_metadata_service.mohpackets.tests.endpoints.base import BaseTestCase
from chord_metadata_service.mohpackets.tests.endpoints.factories import DonorFactory


# DONOR API
# ---------
class DonorAPITestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.donor_url = "/v2/ingest/donors/"

    def test_donor_create_authorized(self):
        """
        Test that an admin user can create a donor and receive 201 Created response.

        Testing Strategy:
        - An authorized user (user_2) with admin permission.
        - User can perform a POST request for donor creation.
        """
        donor_data = DonorFactory.build_batch(program_id=self.programs[0], size=2)
        serialized_data = DonorSerializer(donor_data, many=True).data
        response = self.client.post(
            self.donor_url,
            data=serialized_data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_donor_create_unauthorized(self):
        """
        Test that a non-admin user attempting to create a donor receives a 403 Forbidden response.

        Testing Strategy:
        - An unauthorized user (user_0) with no permission.
        - User cannot perform a POST request for donor creation.
        """
        donor_data = DonorFactory.build_batch(program_id=self.programs[0], size=2)
        serialized_data = DonorSerializer(donor_data, many=True).data
        response = self.client.post(
            self.donor_url,
            data=serialized_data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.user_0.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
