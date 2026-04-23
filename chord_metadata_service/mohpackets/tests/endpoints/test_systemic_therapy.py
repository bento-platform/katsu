from http import HTTPStatus

from django.conf import settings
from django.forms.models import model_to_dict

from chord_metadata_service.mohpackets.models import SystemicTherapy
from chord_metadata_service.mohpackets.tests.endpoints.base import BaseTestCase
from chord_metadata_service.mohpackets.tests.factories import (
    SystemicTherapyFactory,
)


# INGEST API
# ----------
class IngestTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.systemic_therapy_url = "/v3/ingest/systemic_therapies/"

    def test_systemic_therapy_create_authorized(self):
        """
        Test that an admin user can create a systemic therapy record and receive 201 Created response.

        Testing Strategy:
        - Build Systemic Therapy data based on the existing treatment
        - An authorized user (user_2) with admin permission.
        - User can perform a POST request for systemic therapy record creation.
        """
        systemic_therapy = SystemicTherapyFactory.build(
            treatment_uuid=self.treatments[0]
        )
        data_dict = model_to_dict(systemic_therapy)
        response = self.client.post(
            self.systemic_therapy_url,
            data=[data_dict],
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

    def test_systemic_therapy_create_unauthorized(self):
        """
        Test that a non-admin user attempting to create a systemic therapy record receives a 403 Forbidden response.

        Testing Strategy:
        - Build systemic therapy data based on the existing treatment
        - An unauthorized user (user_0) with no permission.
        - User cannot perform a POST request for systemic therapy record creation.
        """
        systemic_therapy = SystemicTherapyFactory.build(
            treatment_uuid=self.treatments[0]
        )
        data_dict = model_to_dict(systemic_therapy)
        response = self.client.post(
            self.systemic_therapy_url,
            data=[data_dict],
            content_type="application/json",
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.user_0.token}",
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_systemic_therapy_ingest_validator(self):
        """
        Test invalid data and receive 422 unprocess response.

        Testing Strategy:
        - Build systemic therapy data based on the existing treatment_uuid and wrong data for validator
        - An authorized user (user_2) with admin permission.
        - User cannot perform a POST request for systemic therapy record creation.
        """
        systemic_therapy = SystemicTherapyFactory.build(
            treatment_uuid=self.treatments[0]
        )
        data_dict = model_to_dict(systemic_therapy)
        data_dict["drug_reference_database"] = "invalid"
        response = self.client.post(
            self.systemic_therapy_url,
            data=[data_dict],
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
        self.systemic_therapy_url = "/v3/authorized/systemic_therapies/"

    def test_get_chemotherapy_200_ok(self):
        """
        Test a successful GET request to the 'authorized' endpoint.

        Testing Strategy:
        - An authorized user (user_1) attempts a GET request for authorized systemic_therapy records.
        - The request should receive a 200 OK response.
        """
        response = self.client.get(
            self.systemic_therapy_url,
            HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_systemic_therapy_301_redirect(self):
        """
        Test a GET request endpoint with a 301 redirection.

        Testing Strategy:
        - Send a GET request to the '/v3/authorized/' endpoint.
        - The request should receive a 301 redirection response.
        """
        response = self.client.get(
            "/v3/authorized/systemic_therapies",
            HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}",
        )
        self.assertEqual(response.status_code, HTTPStatus.MOVED_PERMANENTLY)

    def test_get_systemic_therapies_filter_by_multiple_drug_names(self):
        """
        Test that filtering by multiple comma-separated drug_names returns OR'd results.
        """
        st1 = self.systemic_therapies[0]
        st1.drug_name = "DrugA"
        st1.save()

        st2 = self.systemic_therapies[1]
        st2.drug_name = "DrugB"
        st2.save()

        st3 = self.systemic_therapies[2]
        st3.drug_name = "DrugC"
        st3.save()

        response = self.client.get(
            f"{self.systemic_therapy_url}?drug_name=DrugA,DrugB",
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.json()["items"]
        returned_drug_names = [st["drug_name"] for st in data]
        self.assertIn(st1.drug_name, returned_drug_names)
        self.assertIn(st2.drug_name, returned_drug_names)
        self.assertNotIn(st3.drug_name, returned_drug_names)


# OTHERS
# ------
class SystemicTherapyOthersTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.systemic_therapy_url = "/v3/authorized/systemic_therapies/"

    def test_get_datasets_match_permission(self):
        """
        Test that the response datasets match the authorized datasets for each user.

        Testing Strategy:
        - Get a list of datasets associated with systemic_therapy records of each user
        - Call the endpoint to get all systemic_therapy records
        - Verify that the response datasets match the datasets in the authorized datasets
          for each of the test users.
        """
        for user in self.users:
            authorized_datasets = settings.LOCAL_OPA_DATASET.get(user.token, {}).get(
                "read_datasets", []
            )
            expected_datasets = [
                str(dataset)
                for dataset in SystemicTherapy.objects.filter(
                    program_id__in=authorized_datasets
                )
            ]

            # get systemic_therapy records' datasets from the API
            response = self.client.get(
                self.systemic_therapy_url,
                HTTP_AUTHORIZATION=f"Bearer {user.token}",
            )
            response = response.json()
            response_data = [
                f'{systemic_therapy["program_id"]}: {systemic_therapy["submitter_treatment_id"]}'
                for systemic_therapy in response["items"]
            ]

            self.assertEqual(response_data, expected_datasets)

    def test_post_request_405(self):
        """
        Test a POST request to the '/authorized/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.post(
            self.systemic_therapy_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_put_request_405(self):
        """
        Test a PUT request to the '/authorized/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.put(
            self.systemic_therapy_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_patch_request_405(self):
        """
        Test a PATCH request to the '/authorized/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.patch(
            self.systemic_therapy_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_delete_request_404(self):
        """
        Test a DELETE request 'authorized/chemotherapy/{id}/' endpoint.

        Testing Strategy:
        - Create a new chemotherapy record to delete
        - The request should receive a 404 response.
        """
        therapy_to_delete = SystemicTherapyFactory()
        response = self.client.delete(
            f"{self.systemic_therapy_url}{therapy_to_delete.uuid}/",
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
