from django.conf import settings
from rest_framework import status

from chord_metadata_service.mohpackets.serializers import ProgramSerializer
from chord_metadata_service.mohpackets.tests.endpoints.base import BaseTestCase
from chord_metadata_service.mohpackets.tests.endpoints.factories import ProgramFactory

"""
    This file contains test cases for Program API endpoints.
    The tests cover various scenarios to ensure proper functionality and authorization
    for API endpoints.

"""


# INGEST API
# ----------
class IngestTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.ingest_url = "/v2/ingest/programs/"

    def test_ingest_authorized(self):
        """
        Test that an admin user can ingest and receive 201 Created response

        Testing Strategy:
        - An authorized user (user_2) with admin permission.
        - User can perform a POST request for program ingestion.
        """
        ingest_programs = ProgramFactory.build_batch(2)
        serialized_data = ProgramSerializer(ingest_programs, many=True).data
        response = self.client.post(
            self.ingest_url,
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

    def test_ingest_unauthorized(self):
        """
        Test that an non-admin user attempting to ingest programs receives a 403 Forbidden response.

        Testing Strategy:
        - An unauthorized user (user_0) with no permission.
        - User cannot perform a POST request for program ingestion.
        """
        ingest_programs = ProgramFactory.build_batch(2)
        serialized_data = ProgramSerializer(ingest_programs, many=True).data
        response = self.client.post(
            self.ingest_url,
            data=serialized_data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.user_0.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# DELETE API
# ----------
class DeleteTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.authorized_url = "/v2/authorized/programs/"

    def test_delete_authorized(self):
        """
        Test an authorized DELETE request to the 'authorized/programs/{program_id}/' endpoint.

        Testing Strategy:
        - Create a new program to delete
        - Admin (user_2) can delete
        - The request should receive a 204 no content response.
        """
        program_to_delete = ProgramFactory()
        response = self.client.delete(
            f"{self.authorized_url}{program_to_delete.program_id}/",
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_unauthorized(self):
        """
        Test an unauthorized DELETE request 'authorized/programs/{program_id}/' endpoint.

        Testing Strategy:
        - Create a new program to delete
        - Non Admin (user_1) cannot delete
        - The request should receive a 403 forbidden response.
        """
        program_to_delete = ProgramFactory()
        response = self.client.delete(
            f"{self.authorized_url}{program_to_delete.program_id}/",
            HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# GET API
# -------
class GETTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.authorized_url = "/v2/authorized/programs/"

    def test_get_200_ok(self):
        """
        Test a successful GET request to the 'authorized/programs/' endpoint.

        Testing Strategy:
        - An authorized user (user_1) attempts a GET request for authorized programs.
        - The request should receive a 200 OK response.
        """
        response = self.client.get(
            self.authorized_url,
            HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_301_redirect(self):
        """
        Test a GET request endpoint with a 301 redirection.

        Testing Strategy:
        - Send a GET request to the '/v2/authorized/programs' endpoint.
        - The request should receive a 301 redirection response.
        """
        response = self.client.get(
            "/v2/authorized/programs", HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_get_404_not_found(self):
        """
        Test a GET request for a 404 Not Found response.

        Testing Strategy:
        - Send a GET request to a non-existent endpoint.
        - The request should receive a 404 Not Found response.
        """
        response = self.client.get(
            "/v2/authorized/invalid/",
            HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# OTHERS
# ------
class OthersTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.authorized_url = "/v2/authorized/programs/"

    def test_get_datasets_match_permission(self):
        """
        Test that the response datasets match the authorized datasets for each user.

        Testing Strategy:
        - Verify that the response datasets match the datasets in the authorized dataset
          for each of the test users.
        """
        for user in self.users:
            response = self.client.get(
                self.authorized_url,
                HTTP_AUTHORIZATION=f"Bearer {user.token}",
            )

            authorized_datasets = next(
                user_data["datasets"]
                for user_data in settings.LOCAL_AUTHORIZED_DATASET
                if user_data["token"] == user.token
            )
            response_datasets = [
                program["program_id"] for program in response.data["results"]
            ]
            self.assertEqual(response_datasets, authorized_datasets)

    def test_post_request_405(self):
        """
        Test a POST request to the '/authorized/programs/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.post(
            self.authorized_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_request_405(self):
        """
        Test a PUT request to the '/authorized/programs/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.put(
            self.authorized_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_request_405(self):
        """
        Test a PATCH request to the '/authorized/programs/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.patch(
            self.authorized_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
