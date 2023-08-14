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
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            f"Expected status code {status.HTTP_201_CREATED}, but got {response.status_code}. "
            f"Response content: {response.content}",
        )

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


# GET API
# -------
class GETTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.sample_registrations_url = "/v2/authorized/sample_registrations/"

    def test_get_sample_registrations_200_ok(self):
        """
        Test a successful GET request to the 'authorized/sample_registrations/' endpoint.

        Testing Strategy:
        - An authorized user (user_1) attempts a GET request for authorized sample registrations.
        - The request should receive a 200 OK response.
        """
        response = self.client.get(
            self.sample_registrations_url,
            HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_sample_registrations_301_redirect(self):
        """
        Test a GET request endpoint with a 301 redirection.

        Testing Strategy:
        - Send a GET request to the '/v2/authorized/sample_registrations' endpoint.
        - The request should receive a 301 redirection response.
        """
        response = self.client.get(
            "/v2/authorized/sample_registrations",
            HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)


# OTHERS
# ------
class OthersTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.sample_registrations_url = "/v2/authorized/sample_registrations/"

    def test_get_datasets_match_permission(self):
        """
        Test that the response datasets match the authorized datasets for each user.

        Testing Strategy:
        - Get a list of datasets associated with sample registrations of each user
        - Call the endpoint to get all sample registrations
        - Verify that the response datasets match the datasets in the authorized datasets
          for each of the test users.
        """
        for user in self.users:
            authorized_datasets = next(
                user_data["datasets"]
                for user_data in settings.LOCAL_AUTHORIZED_DATASET
                if user_data["token"] == user.token
            )
            # get sample registrations' datasets from the database
            expected_datasets = list(
                SampleRegistration.objects.filter(
                    program_id__in=authorized_datasets
                ).values_list("submitter_sample_id", flat=True)
            )

            # get sample registrations' datasets from the API
            response = self.client.get(
                self.sample_registrations_url,
                HTTP_AUTHORIZATION=f"Bearer {user.token}",
            )
            response_data = [
                sample_registration["submitter_sample_id"]
                for sample_registration in response.data["results"]
            ]

            self.assertEqual(response_data, expected_datasets)

    def test_post_request_405(self):
        """
        Test a POST request to the '/authorized/sample-registrations/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.post(
            self.sample_registrations_url,
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_request_405(self):
        """
        Test a PUT request to the '/authorized/sample-registrations/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.put(
            self.sample_registrations_url,
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_request_405(self):
        """
        Test a PATCH request to the '/authorized/sample-registrations/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.patch(
            self.sample_registrations_url,
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_request_404(self):
        """
        Test a DELETE request 'authorized/sample-registrations/{id}/' endpoint.

        Testing Strategy:
        - Create a new sample registration to delete
        - The request should receive a 404 response.
        """
        sample_registration_to_delete = SampleRegistrationFactory()
        response = self.client.delete(
            f"{self.sample_registrations_url}{sample_registration_to_delete.submitter_sample_id}/",
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
