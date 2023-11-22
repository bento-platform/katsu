from http import HTTPStatus

from django.conf import settings
from django.forms.models import model_to_dict

from chord_metadata_service.mohpackets.models import Chemotherapy
from chord_metadata_service.mohpackets.tests.endpoints.base import BaseTestCase
from chord_metadata_service.mohpackets.tests.endpoints.factories import (
    ChemotherapyFactory,
)


# INGEST API
# ----------
class IngestTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.chemotherapy_url = "/v2/ingest/chemotherapy/"

    def test_chemotherapy_create_authorized(self):
        """
        Test that an admin user can create a chemotherapy record and receive 201 Created response.

        Testing Strategy:
        - Build Chemotherapy data based on the existing primary_diagnosis_id
        - An authorized user (user_2) with admin permission.
        - User can perform a POST request for chemotherapy record creation.
        """
        chemotherapy = ChemotherapyFactory.build(treatment_uuid=self.treatments[0])
        data_dict = model_to_dict(chemotherapy)
        response = self.client.post(
            self.chemotherapy_url,
            data=data_dict,
            format="json",
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.CREATED,
            f"Expected status code {HTTPStatus.CREATED}, but got {response.status_code}. "
            f"Response content: {response.content}",
        )

    def test_chemotherapy_create_unauthorized(self):
        """
        Test that a non-admin user attempting to create a chemotherapy record receives a 403 Forbidden response.

        Testing Strategy:
        - Build Chemotherapy data based on the existing primary_diagnosis_id
        - An unauthorized user (user_0) with no permission.
        - User cannot perform a POST request for chemotherapy record creation.
        """
        chemotherapy = ChemotherapyFactory.build(treatment_uuid=self.treatments[0])
        data_dict = model_to_dict(chemotherapy)
        response = self.client.post(
            self.chemotherapy_url,
            data=data_dict,
            content_type="application/json",
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.user_0.token}",
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)


# GET API
# -------
class GETTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.chemotherapy_url = "/v2/authorized/chemotherapies/"

    def test_get_chemotherapy_200_ok(self):
        """
        Test a successful GET request to the 'authorized/chemotherapy/' endpoint.

        Testing Strategy:
        - An authorized user (user_1) attempts a GET request for authorized chemotherapy records.
        - The request should receive a 200 OK response.
        """
        response = self.client.get(
            self.chemotherapy_url,
            HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_chemotherapy_301_redirect(self):
        """
        Test a GET request endpoint with a 301 redirection.

        Testing Strategy:
        - Send a GET request to the '/v2/authorized/chemotherapies' endpoint.
        - The request should receive a 301 redirection response.
        """
        response = self.client.get(
            "/v2/authorized/chemotherapies",
            HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}",
        )
        self.assertEqual(response.status_code, HTTPStatus.MOVED_PERMANENTLY)


# OTHERS
# ------
class ChemotherapyOthersTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.chemotherapy_url = "/v2/authorized/chemotherapies/"

    def test_get_datasets_match_permission(self):
        """
        Test that the response datasets match the authorized datasets for each user.

        Testing Strategy:
        - Get a list of datasets associated with chemotherapy records of each user
        - Call the endpoint to get all chemotherapy records
        - Verify that the response datasets match the datasets in the authorized datasets
          for each of the test users.
        """
        for user in self.users:
            authorized_datasets = next(
                user_data["datasets"]
                for user_data in settings.LOCAL_AUTHORIZED_DATASET
                if user_data["token"] == user.token
            )
            expected_datasets = [
                str(dataset)
                for dataset in Chemotherapy.objects.filter(
                    program_id__in=authorized_datasets
                )
            ]

            # get chemotherapy records' datasets from the API
            response = self.client.get(
                self.chemotherapy_url,
                HTTP_AUTHORIZATION=f"Bearer {user.token}",
            )
            response = response.json()
            response_data = [
                f'{chemotherapy["program_id"]}: {chemotherapy["submitter_treatment_id"]}'
                for chemotherapy in response["items"]
            ]

            self.assertEqual(response_data, expected_datasets)

    def test_post_request_405(self):
        """
        Test a POST request to the '/authorized/chemotherapy/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.post(
            self.chemotherapy_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_put_request_405(self):
        """
        Test a PUT request to the '/authorized/chemotherapy/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.put(
            self.chemotherapy_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_patch_request_405(self):
        """
        Test a PATCH request to the '/authorized/chemotherapy/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.patch(
            self.chemotherapy_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_delete_request_404(self):
        """
        Test a DELETE request 'authorized/chemotherapy/{id}/' endpoint.

        Testing Strategy:
        - Create a new chemotherapy record to delete
        - The request should receive a 404 response.
        """
        chemotherapy_to_delete = ChemotherapyFactory()
        response = self.client.delete(
            f"{self.chemotherapy_url}{chemotherapy_to_delete.uuid}/",
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
