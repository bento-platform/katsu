import factory
from django.conf import settings
from rest_framework import status

from chord_metadata_service.mohpackets.models import PrimaryDiagnosis
from chord_metadata_service.mohpackets.serializers import PrimaryDiagnosisSerializer
from chord_metadata_service.mohpackets.tests.endpoints.base import BaseTestCase
from chord_metadata_service.mohpackets.tests.endpoints.factories import (
    PrimaryDiagnosisFactory,
)


# INGEST API
# ----------
class IngestTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.primary_diagnosis_url = "/v2/ingest/primary_diagnoses/"

    def test_primary_diagnosis_create_authorized(self):
        """
        Test that an admin user can create a primary diagnosis and receive 201 Created response.

        Testing Strategy:
        - Build PrimaryDiagnosis data based on the existing donor_id
        - An authorized user (user_2) with admin permission.
        - User can perform a POST request for primary diagnosis creation.
        """
        primary_diagnosis_data = PrimaryDiagnosisFactory.build_batch(
            submitter_donor_id=factory.Iterator(self.donors), size=2
        )
        serialized_data = PrimaryDiagnosisSerializer(
            primary_diagnosis_data, many=True
        ).data
        response = self.client.post(
            self.primary_diagnosis_url,
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

    def test_primary_diagnosis_create_unauthorized(self):
        """
        Test that a non-admin user attempting to create a primary diagnosis receives a 403 Forbidden response.

        Testing Strategy:
        - Build PrimaryDiagnosis data based on the existing program_id
        - An unauthorized user (user_0) with no permission.
        - User cannot perform a POST request for primary diagnosis creation.
        """
        primary_diagnosis_data = PrimaryDiagnosisFactory.build_batch(
            submitter_donor_id=factory.Iterator(self.donors), size=2
        )
        serialized_data = PrimaryDiagnosisSerializer(
            primary_diagnosis_data, many=True
        ).data
        response = self.client.post(
            self.primary_diagnosis_url,
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
        self.primary_diagnosis_url = "/v2/authorized/primary_diagnoses/"

    def test_get_primary_diagnosis_200_ok(self):
        """
        Test a successful GET request to the 'authorized/primary_diagnoses/' endpoint.

        Testing Strategy:
        - An authorized user (user_1) attempts a GET request for authorized primary diagnoses.
        - The request should receive a 200 OK response.
        """
        response = self.client.get(
            self.primary_diagnosis_url,
            HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_primary_diagnosis_301_redirect(self):
        """
        Test a GET request endpoint with a 301 redirection.

        Testing Strategy:
        - Send a GET request to the '/v2/authorized/primary_diagnoses' endpoint.
        - The request should receive a 301 redirection response.
        """
        response = self.client.get(
            "/v2/authorized/primary_diagnoses",
            HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)


# OTHERS
# ------
class OthersTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.primary_diagnosis_url = "/v2/authorized/primary_diagnoses/"

    def test_get_datasets_match_permission(self):
        """
        Test that the response datasets match the authorized datasets for each user.

        Testing Strategy:
        - Get a list of primary diagnoses associated with datasets of each user
        - Call the endpoint to get all primary diagnoses
        - Verify that the response datasets match the primary diagnoses in the authorized datasets
          for each of the test users.
        """
        for user in self.users:
            authorized_datasets = next(
                user_data["datasets"]
                for user_data in settings.LOCAL_AUTHORIZED_DATASET
                if user_data["token"] == user.token
            )
            # get primary diagnoses from the database
            expected_primary_diagnoses = list(
                PrimaryDiagnosis.objects.filter(
                    program_id__in=authorized_datasets
                ).values_list("submitter_primary_diagnosis_id", flat=True)
            )

            # get primary diagnoses from the api
            response = self.client.get(
                self.primary_diagnosis_url,
                HTTP_AUTHORIZATION=f"Bearer {user.token}",
            )
            response_data = [
                primary_diagnosis["submitter_primary_diagnosis_id"]
                for primary_diagnosis in response.data["results"]
            ]

            self.assertEqual(response_data, expected_primary_diagnoses)

    def test_post_request_405(self):
        """
        Test a POST request to the '/authorized/primary_diagnoses/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.post(
            self.primary_diagnosis_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_request_405(self):
        """
        Test a PUT request to the '/authorized/primary_diagnoses/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.put(
            self.primary_diagnosis_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_request_405(self):
        """
        Test a PATCH request to the '/authorized/primary_diagnoses/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.patch(
            self.primary_diagnosis_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_request_404(self):
        """
        Test a DELETE request 'authorized/primary_diagnoses/{id}/' endpoint.

        Testing Strategy:
        - Create a new diagnoses to delete
        - The request should receive a 404 response.
        """
        diagnoses_to_delete = PrimaryDiagnosisFactory()
        response = self.client.delete(
            f"{self.primary_diagnosis_url}{diagnoses_to_delete.submitter_primary_diagnosis_id}/",
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
