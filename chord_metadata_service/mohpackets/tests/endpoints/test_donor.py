import factory
from django.conf import settings
from rest_framework import status

from chord_metadata_service.mohpackets.models import Donor
from chord_metadata_service.mohpackets.serializers import DonorSerializer
from chord_metadata_service.mohpackets.tests.endpoints.base import BaseTestCase
from chord_metadata_service.mohpackets.tests.endpoints.factories import DonorFactory


# INGEST API
# ----------
class IngestTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.donor_url = "/v2/ingest/donors/"

    def test_donor_create_authorized(self):
        """
        Test that an admin user can create a donor and receive 201 Created response.

        Testing Strategy:
        - Build Donor data based on the existing program_id
        - An authorized user (user_2) with admin permission.
        - User can perform a POST request for donor creation.
        """
        donor_data = DonorFactory.build_batch(
            program_id=factory.Iterator(self.programs), size=2
        )
        serialized_data = DonorSerializer(donor_data, many=True).data
        response = self.client.post(
            self.donor_url,
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

    def test_donor_create_unauthorized(self):
        """
        Test that a non-admin user attempting to create a donor receives a 403 Forbidden response.

        Testing Strategy:
        - Build Donor data based on the existing program_id
        - An unauthorized user (user_0) with no permission.
        - User cannot perform a POST request for donor creation.
        """
        donor_data = DonorFactory.build_batch(
            program_id=factory.Iterator(self.programs), size=2
        )
        serialized_data = DonorSerializer(donor_data, many=True).data
        response = self.client.post(
            self.donor_url,
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
        self.donor_url = "/v2/authorized/donors/"

    def test_get_donor_200_ok(self):
        """
        Test a successful GET request to the 'authorized/donors/' endpoint.

        Testing Strategy:
        - An authorized user (user_1) attempts a GET request for authorized donors.
        - The request should receive a 200 OK response.
        """
        response = self.client.get(
            self.donor_url,
            HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_donor_301_redirect(self):
        """
        Test a GET request endpoint with a 301 redirection.

        Testing Strategy:
        - Send a GET request to the '/v2/authorized/donors' endpoint.
        - The request should receive a 301 redirection response.
        """
        response = self.client.get(
            "/v2/authorized/donors", HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)


# OTHERS
# ------
class OthersTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.donor_url = "/v2/authorized/donors/"

    def test_get_datasets_match_permission(self):
        """
        Test that the response datasets match the authorized datasets for each user.

        Testing Strategy:
        - Get a list of donors associated with datasets of each user
        - Call the endpoint to get all donors
        - Verify that the response datasets match the donors in the authorized datasets
          for each of the test users.
        """
        for user in self.users:
            authorized_datasets = next(
                user_data["datasets"]
                for user_data in settings.LOCAL_AUTHORIZED_DATASET
                if user_data["token"] == user.token
            )
            # get donors from the database
            expected_donors = list(
                Donor.objects.filter(program_id__in=authorized_datasets).values_list(
                    "submitter_donor_id", flat=True
                )
            )

            # get donors from the api
            response = self.client.get(
                self.donor_url,
                HTTP_AUTHORIZATION=f"Bearer {user.token}",
            )
            response_data = [
                donor["submitter_donor_id"] for donor in response.data["results"]
            ]

            self.assertEqual(response_data, expected_donors)

    def test_post_request_405(self):
        """
        Test a POST request to the '/authorized/donors/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.post(
            self.donor_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_request_405(self):
        """
        Test a PUT request to the '/authorized/donors/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.put(
            self.donor_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_request_405(self):
        """
        Test a PATCH request to the '/authorized/donors/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.patch(
            self.donor_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_request_404(self):
        """
        Test a DELETE request 'authorized/donors/{id}/' endpoint.

        Testing Strategy:
        - Create a new donors to delete
        - The request should receive a 404 response.
        """
        donor_to_delete = DonorFactory()
        response = self.client.delete(
            f"{self.donor_url}{donor_to_delete.submitter_donor_id}/",
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
