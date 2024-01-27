from http import HTTPStatus

from django.conf import settings
from django.forms.models import model_to_dict

from chord_metadata_service.mohpackets.models import Specimen
from chord_metadata_service.mohpackets.tests.endpoints.base import BaseTestCase
from chord_metadata_service.mohpackets.tests.endpoints.factories import SpecimenFactory


# INGEST API
# ----------
class IngestTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.specimen_url = "/v2/ingest/specimen/"

    def test_specimen_create_authorized(self):
        """
        Test that an admin user can create a specimen and receive 201 Created response.

        Testing Strategy:
        - Build Specimen data based on the existing donor_id
        - An authorized user (user_2) with admin permission.
        - User can perform a POST request for specimen creation.
        """
        specimen = SpecimenFactory.build(
            primary_diagnosis_uuid=self.primary_diagnoses[0]
        )
        data_dict = model_to_dict(specimen)
        response = self.client.post(
            self.specimen_url,
            data=data_dict,
            content_type="application/json",
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.CREATED,
            f"Expected status code {HTTPStatus.CREATED}, but got {response.status_code}. "
            f"Response content: {response.content}",
        )

    def test_specimen_create_unauthorized(self):
        """
        Test that a non-admin user attempting to create a specimen receives a 403 Forbidden response.

        Testing Strategy:
        - Build Specimen data based on the existing donor_id
        - An unauthorized user (user_0) with no permission.
        - User cannot perform a POST request for specimen creation.
        """
        specimen = SpecimenFactory.build(
            primary_diagnosis_uuid=self.primary_diagnoses[0]
        )
        data_dict = model_to_dict(specimen)
        response = self.client.post(
            self.specimen_url,
            data=data_dict,
            content_type="application/json",
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.user_0.token}",
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_specimen_ingest_validator(self):
        """
        Test invalid data and receive 422 unprocess response.

        Testing Strategy:
        - Build Specimen data based on the existing primary_diagnosis_uuid and wrong data for validator
        - An authorized user (user_2) with admin permission.
        - User cannot perform a POST request for specimen creation.
        """
        specimen = SpecimenFactory.build(
            primary_diagnosis_uuid=self.primary_diagnoses[0]
        )
        specimen_dict = model_to_dict(specimen)
        specimen_dict["tumour_grade"] = "invalid"
        response = self.client.post(
            self.specimen_url,
            data=specimen_dict,
            content_type="application/json",
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.UNPROCESSABLE_ENTITY,
            f"Expected status code {HTTPStatus.UNPROCESSABLE_ENTITY}, but got {response.status_code}. "
            f"Response content: {response.content}",
        )


# GET API
# -------
class GETTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.specimen_url = "/v2/authorized/specimens/"

    def test_get_specimen_200_ok(self):
        """
        Test a successful GET request to the 'authorized/specimen/' endpoint.

        Testing Strategy:
        - An authorized user (user_1) attempts a GET request for authorized specimens.
        - The request should receive a 200 OK response.
        """
        response = self.client.get(
            self.specimen_url,
            HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_specimen_301_redirect(self):
        """
        Test a GET request endpoint with a 301 redirection.

        Testing Strategy:
        - Send a GET request to the '/v2/authorized/specimen' endpoint.
        - The request should receive a 301 redirection response.
        """
        response = self.client.get(
            "/v2/authorized/specimens",
            HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}",
        )
        self.assertEqual(response.status_code, HTTPStatus.MOVED_PERMANENTLY)


# OTHERS
# ------
class OthersTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.specimen_url = "/v2/authorized/specimens/"

    def test_get_datasets_match_permission(self):
        """
        Test that the response datasets match the authorized datasets for each user.

        Testing Strategy:
        - Get a list of specimens associated with datasets of each user
        - Call the endpoint to get all specimens
        - Verify that the response datasets match the specimens in the authorized datasets
          for each of the test users.
        """
        for user in self.users:
            authorized_datasets = next(
                user_data["datasets"]
                for user_data in settings.LOCAL_AUTHORIZED_DATASET
                if user_data["token"] == user.token
            )
            # get specimens from the database
            # get primary diagnoses from the database
            expected_specimens = list(
                Specimen.objects.filter(program_id__in=authorized_datasets).values_list(
                    "submitter_specimen_id", flat=True
                )
            )

            # get specimens from the api
            response = self.client.get(
                self.specimen_url,
                HTTP_AUTHORIZATION=f"Bearer {user.token}",
            )
            response = response.json()
            response_data = [
                specimen["submitter_specimen_id"] for specimen in response["items"]
            ]

            self.assertEqual(response_data, expected_specimens)

    def test_post_request_405(self):
        """
        Test a POST request to the '/authorized/specimens/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.post(
            self.specimen_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_put_request_405(self):
        """
        Test a PUT request to the '/authorized/specimens/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.put(
            self.specimen_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_patch_request_405(self):
        """
        Test a PATCH request to the '/authorized/specimens/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.patch(
            self.specimen_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_delete_request_404(self):
        """
        Test a DELETE request 'authorized/specimens/{id}/' endpoint.

        Testing Strategy:
        - Create a new specimen to delete
        - The request should receive a 404 response.
        """
        specimen_to_delete = SpecimenFactory()
        response = self.client.delete(
            f"{self.specimen_url}{specimen_to_delete.submitter_specimen_id}/",
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
