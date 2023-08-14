import factory
from django.conf import settings
from rest_framework import status

from chord_metadata_service.mohpackets.models import Treatment
from chord_metadata_service.mohpackets.serializers import TreatmentSerializer
from chord_metadata_service.mohpackets.tests.endpoints.base import BaseTestCase
from chord_metadata_service.mohpackets.tests.endpoints.factories import TreatmentFactory


# INGEST API
# ----------
class TreatmentsIngestTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.treatment_url = "/v2/ingest/treatments/"

    def test_treatment_create_authorized(self):
        """
        Test that an admin user can create a treatment and receive 201 Created response.

        Testing Strategy:
        - Build Treatment data based on the existing donor_id
        - An authorized user (user_2) with admin permission.
        - User can perform a POST request for treatment creation.
        """
        treatment_data = TreatmentFactory.build_batch(
            submitter_primary_diagnosis_id=factory.Iterator(self.primary_diagnoses),
            size=2,
        )
        serialized_data = TreatmentSerializer(treatment_data, many=True).data
        response = self.client.post(
            self.treatment_url,
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

    def test_treatment_create_unauthorized(self):
        """
        Test that a non-admin user attempting to create a treatment receives a 403 Forbidden response.

        Testing Strategy:
        - Build Treatment data based on the existing donor_id
        - An unauthorized user (user_0) with no permission.
        - User cannot perform a POST request for treatment creation.
        """
        treatment_data = TreatmentFactory.build_batch(
            submitter_primary_diagnosis_id=factory.Iterator(self.primary_diagnoses),
            size=2,
        )
        serialized_data = TreatmentSerializer(treatment_data, many=True).data
        response = self.client.post(
            self.treatment_url,
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
        self.treatments_url = "/v2/authorized/treatments/"

    def test_get_treatments_200_ok(self):
        """
        Test a successful GET request to the 'authorized/treatments/' endpoint.

        Testing Strategy:
        - An authorized user (user_1) attempts a GET request for authorized treatments.
        - The request should receive a 200 OK response.
        """
        response = self.client.get(
            self.treatments_url,
            HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_treatments_301_redirect(self):
        """
        Test a GET request endpoint with a 301 redirection.

        Testing Strategy:
        - Send a GET request to the '/v2/authorized/treatments' endpoint.
        - The request should receive a 301 redirection response.
        """
        response = self.client.get(
            "/v2/authorized/treatments",
            HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)


# OTHERS
# ------
class TreatmentsOthersTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.treatments_url = "/v2/authorized/treatments/"

    def test_get_datasets_match_permission(self):
        """
        Test that the response datasets match the authorized datasets for each user.

        Testing Strategy:
        - Get a list of datasets associated with treatments of each user
        - Call the endpoint to get all treatments
        - Verify that the response datasets match the datasets in the authorized datasets
          for each of the test users.
        """
        for user in self.users:
            authorized_datasets = next(
                user_data["datasets"]
                for user_data in settings.LOCAL_AUTHORIZED_DATASET
                if user_data["token"] == user.token
            )
            # get treatments' datasets from the database
            expected_datasets = list(
                Treatment.objects.filter(
                    program_id__in=authorized_datasets
                ).values_list("submitter_treatment_id", flat=True)
            )

            # get treatments' datasets from the API
            response = self.client.get(
                self.treatments_url,
                HTTP_AUTHORIZATION=f"Bearer {user.token}",
            )
            response_data = [
                treatment["submitter_treatment_id"]
                for treatment in response.data["results"]
            ]

            self.assertEqual(response_data, expected_datasets)

    def test_post_request_405(self):
        """
        Test a POST request to the '/authorized/treatments/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.post(
            self.treatments_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_request_405(self):
        """
        Test a PUT request to the '/authorized/treatments/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.put(
            self.treatments_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_request_405(self):
        """
        Test a PATCH request to the '/authorized/treatments/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.patch(
            self.treatments_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_request_404(self):
        """
        Test a DELETE request 'authorized/treatments/{id}/' endpoint.

        Testing Strategy:
        - Create a new treatment to delete
        - The request should receive a 404 response.
        """
        treatment_to_delete = TreatmentFactory()
        response = self.client.delete(
            f"{self.treatments_url}{treatment_to_delete.submitter_treatment_id}/",
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
