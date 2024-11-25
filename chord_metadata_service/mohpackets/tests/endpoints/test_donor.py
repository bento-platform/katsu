from http import HTTPStatus

from django.conf import settings
from django.forms.models import model_to_dict

from chord_metadata_service.mohpackets.models import Donor
from chord_metadata_service.mohpackets.tests.endpoints.base import BaseTestCase
from chord_metadata_service.mohpackets.tests.factories import DonorFactory

"""
    This module contains API tests related to the Donor model endpoints.

    It includes tests for:
    - Ingesting new donors
    - GET requests
    - Filtering donors by various criteria
    - Explorer API requests
    - Authorization checks for different user roles

    Author: Son Chau
"""


# INGEST API
# ----------
class IngestTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.donor_url = "/v3/ingest/donors/"

    def test_donor_create_authorized(self):
        """
        Test that an admin user can create a donor and receive 201 Created response.

        Testing Strategy:
        - Build Donor data based on the existing program_id
        - An authorized user (user_2) with admin permission.
        - User can perform a POST request for donor creation.
        """
        donor = DonorFactory.build(program_id=self.programs[0])
        data_dict = model_to_dict(donor)
        response = self.client.post(
            self.donor_url,
            data=[data_dict],
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

    def test_donor_create_unauthorized(self):
        """
        Test that a non-admin user attempting to create a donor receives a 401 response.

        Testing Strategy:
        - Build Donor data based on the existing program_id
        - An unauthorized user (user_0) with no permission.
        - User cannot perform a POST request for donor creation.
        """
        donor = DonorFactory.build(program_id=self.programs[0])
        data_dict = model_to_dict(donor)
        response = self.client.post(
            self.donor_url,
            data=[data_dict],
            content_type="application/json",
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.user_0.token}",
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_donor_ingest_validator(self):
        """
        Test invalid data and receive 422 unprocess response.

        Testing Strategy:
        - Build Donor data based on the existing program_id and wrong data for validator
        - An authorized user (user_2) with admin permission.
        - User cannot perform a POST request for donor creation.
        """
        donor = DonorFactory.build(program_id=self.programs[0])
        data_dict = model_to_dict(donor)
        data_dict["cause_of_death"] = "invalid"
        response = self.client.post(
            self.donor_url,
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
        self.donor_url = "/v3/authorized/donors/"

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
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_donor_301_redirect(self):
        """
        Test a GET request endpoint with a 301 redirection.

        Testing Strategy:
        - Send a GET request to the '/v3/authorized/donors' endpoint.
        - The request should receive a 301 redirection response.
        """
        response = self.client.get(
            "/v3/authorized/donors", HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}"
        )
        self.assertEqual(response.status_code, HTTPStatus.MOVED_PERMANENTLY)


# OTHERS
# ------
class OthersTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.donor_url = "/v3/authorized/donors/"

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
            authorized_datasets = settings.LOCAL_OPA_DATASET.get(user.token, {}).get(
                "read_datasets", []
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
            response = response.json()
            response_data = [donor["submitter_donor_id"] for donor in response["items"]]

            self.assertEqual(response_data, expected_donors)

    def test_post_request_405(self):
        """
        Test a POST request to the '/authorized/donors/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.post(
            self.donor_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_put_request_405(self):
        """
        Test a PUT request to the '/authorized/donors/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.put(
            self.donor_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_patch_request_405(self):
        """
        Test a PATCH request to the '/authorized/donors/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.patch(
            self.donor_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

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
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


# EXPLORER API
# ------------
class DonorExplorerTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.donor_url = "/v3/explorer/donors/"

    def test_request_not_from_query(self):
        """
        Verifies that a request made with an invalid query service token
        receives an unauthorized response (HTTP status code 401).

        Testing Strategy:
        - Send a request with an invalid query service token.
        - Ensure that the response status code is 401 (Unauthorized).
        """

        response = self.client.get(
            self.donor_url,
            HTTP_X_SERVICE_TOKEN="invalid_token",
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_request_from_query(self):
        """
        Verifies that a request made with a query service token
        receives a successful response (HTTP status code 200).

        Testing Strategy:
        - Send a request with a query service token.
        - Ensure that the response status code is 200 (OK).
        """

        response = self.client.get(
            self.donor_url,
            HTTP_X_SERVICE_TOKEN=settings.QUERY_SERVICE_TOKEN,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_with_no_filter(self):
        """
        Test request without applying any filters.
        Verifies request returns all donors as expected.

        Testing Strategy:
        - Send a valid request with no filter applied.
        - Confirm the expected count of programs, donors, and sample registrations.
        - 2 programs, 4 donors, and 32 sample registrations
        """
        response = self.client.get(
            self.donor_url,
            HTTP_X_SERVICE_TOKEN=settings.QUERY_SERVICE_TOKEN,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        donors = response.json()

        # Calculate the number of unique programs
        programs = {donor["program_id"] for donor in donors}
        self.assertEqual(len(programs), 2)  # 2 programs

        # Confirm the number of donors
        self.assertEqual(len(donors), 4)  # 4 donors

        # Calculate the total number of sample registrations
        sample_registrations = sum(
            len(donor["submitter_sample_ids"]) for donor in donors
        )
        self.assertEqual(sample_registrations, 32)  # 32 sample registrations

    def test_filter_programs(self):
        """
        Test filtering donors by program.
        Verifies the correct count of donors, excluding a specified program.

        Testing Strategy:
        - Send a valid request with a filter to exclude a specific program.
        - Confirm the expected count of programs, donors, and sample registrations.
        - 1 program, 2 donors, and 16 sample registrations
        """
        response = self.client.get(
            self.donor_url,
            {"exclude_programs": [self.programs[0].program_id]},  # exclude the first one
            HTTP_X_SERVICE_TOKEN=settings.QUERY_SERVICE_TOKEN,
        )
        donors = response.json()

        # Calculate the number of unique programs
        programs = {donor["program_id"] for donor in donors}
        self.assertEqual(len(programs), 1)  # 1 program

        # Confirm the number of donors
        self.assertEqual(len(donors), 2)  # 2 donors

        # Calculate the total number of sample registrations
        sample_registrations = sum(
            len(donor["submitter_sample_ids"]) for donor in donors
        )
        self.assertEqual(sample_registrations, 16)  # 16 sample registrations

    def test_filter_primary_sites(self):
        """
        Test filtering donors by primary site.
        Verifies the correct count of primary site.

        Testing Strategy:
        - Extract the primary site from the first primary diagnosis.
        - Count the number of that primary site in the db
        - Send a valid request with a filter on the primary site.
        - Ensure that the count of returned matches the expected count.
        - Check each returned donor to confirm that it contains the specified primary site.
        """
        selected_primary_site = self.primary_diagnoses[0].primary_site

        # Calculate total count of the primary_site in all primary diagnoses
        primary_site_count = sum(
            1
            for pd in self.primary_diagnoses
            if selected_primary_site == pd.primary_site
        )

        response = self.client.get(
            self.donor_url,
            {"primary_site": [selected_primary_site]},
            HTTP_X_SERVICE_TOKEN=settings.QUERY_SERVICE_TOKEN,
        )
        donors = response.json()

        # Calculate count of primary_site for returned donors
        response_primary_site_count = sum(
            1 for donor in donors if selected_primary_site in donor["primary_site"]
        )

        self.assertEqual(primary_site_count, response_primary_site_count)

        # Check each returned donor to confirm that it contains the specified primary site
        for donor in donors:
            self.assertIn(selected_primary_site, donor["primary_site"])

    def test_filter_treatment_type(self):
        """
        Test the filtering donors by treatment type.
        Verifies the correct count of treatment type from return donors,
        including repeated treatment types.

        Testing Strategy:
        - Extract treatment type from the first treatment.
        - Calculate the total count of the treatment type in all treatments.
        - Send a valid request with a filter on the treatment type.
        - Ensure that the count of treatment type for returned donors matches the expected count.
        """
        selected_treatment_type = self.treatments[0].treatment_type

        # Calculate total count of the treatment type in all treatments
        treatment_type_count = sum(
            1
            for treatment in self.treatments
            if selected_treatment_type in treatment.treatment_type
        )

        response = self.client.get(
            self.donor_url,
            {"treatment_type": [selected_treatment_type]},
            HTTP_X_SERVICE_TOKEN=settings.QUERY_SERVICE_TOKEN,
        )
        donors = response.json()

        # Calculate count of treatment type for returned donors
        response_treatment_type_count = sum(
            1 for donor in donors if selected_treatment_type in donor["treatment_type"]
        )

        self.assertEqual(treatment_type_count, response_treatment_type_count)

    def test_filter_one_drug_name(self):
        """
        Test filtering donors by a drug name.
        Verifies the correct count of return donors.

        Testing Strategy:
        - Extract drug name from the first systemic therapy.
        - Collect distinct donors associated with the specified drug name.
        - Send a valid request with a filter on the drug name.
        - Ensure that the count of returned donors matches the expected count.
        """
        selected_drug_name = self.systemic_therapies[0].drug_name

        donors_with_selected_drug_name = {
            systemic_therapy.treatment_uuid.donor_uuid_id
            for systemic_therapy in self.systemic_therapies
            if systemic_therapy.drug_name == selected_drug_name
        }

        response = self.client.get(
            self.donor_url,
            {"systemic_therapy_drug_name": [selected_drug_name]},
            HTTP_X_SERVICE_TOKEN=settings.QUERY_SERVICE_TOKEN,
        )
        donors = response.json()

        assert len(donors) == len(donors_with_selected_drug_name)

    def test_filter_two_drug_names(self):
        """
        Test filtering donors by 2 drug names.
        Verifies the correct count of return donors.

        Testing Strategy:
        - Extract 2 drug names from systemic therapies.
        - Collect donors associated with each drug name.
        - Send a valid request with a filter on both drug names.
        - Ensure that the count of returned donors matches the expected count.
        """
        selected_drug_names = [
            therapy.drug_name for therapy in self.systemic_therapies[:2]
        ]

        donors_with_selected_drug_names = set()
        for systemic_therapy in self.systemic_therapies:
            if systemic_therapy.drug_name in selected_drug_names:
                donors_with_selected_drug_names.add(
                    systemic_therapy.treatment_uuid.donor_uuid_id
                )

        response = self.client.get(
            self.donor_url,
            {"systemic_therapy_drug_name": selected_drug_names},
            HTTP_X_SERVICE_TOKEN=settings.QUERY_SERVICE_TOKEN,
        )
        donors = response.json()

        assert len(donors) == len(donors_with_selected_drug_names)

    def test_donor_with_missing_data(self):
        """
        Test donor with missing data.
        Verifies that the API can still return the donor correctly.

        Testing Strategy:
        - Add a new donor without anything (e.g sample registrations or treatments)
        - Send a valid request with no filters.
        - Ensure that the response contains the donor with empty submitter_sample_ids and treatment_type.
        """

        DonorFactory.create(
            program_id=self.programs[0], submitter_donor_id="DONOR_MISSING_DATA"
        )

        response = self.client.get(
            self.donor_url,
            HTTP_X_SERVICE_TOKEN=settings.QUERY_SERVICE_TOKEN,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        missing_data_donor = next(
            (
                donor
                for donor in response.json()
                if donor["submitter_donor_id"] == "DONOR_MISSING_DATA"
            ),
            None,  # Default value if donor is not found
        )
        self.assertIsNotNone(
            missing_data_donor, "Donor with missing data  not found in response"
        )
        self.assertIsNone(missing_data_donor["submitter_sample_ids"])
        self.assertEqual(missing_data_donor["treatment_type"], [])


# QUERY API
# ------------
class DonorQueryTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.donor_url = "/v3/authorized/query/"

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
            authorized_datasets = settings.LOCAL_OPA_DATASET.get(user.token, {}).get(
                "read_datasets", []
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
            response = response.json()
            response_data = [donor["submitter_donor_id"] for donor in response["items"]]

            self.assertEqual(sorted(response_data), sorted(expected_donors))

    def test_post_request_405(self):
        """
        Test a POST request to the '/authorized/query/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.post(
            self.donor_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_put_request_405(self):
        """
        Test a PUT request to the '/authorized/query/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.put(
            self.donor_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_patch_request_405(self):
        """
        Test a PATCH request to the '/authorized/query/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.patch(
            self.donor_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_delete_request_405(self):
        """
        Test a DELETE request to the '/authorized/query/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.delete(
            self.donor_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_filter_programs(self):
        """
        Test filtering donors by program.
        Verifies the correct count of donors, excluding a specified program.

        Testing Strategy:
        - Send a valid request with a filter to exclude a specific program.
        - Confirm the expected count of programs, donors, and sample registrations.
        - 1 program, 2 donors, and 16 sample registrations
        """
        response = self.client.get(
            self.donor_url,
            {"exclude_programs": [self.programs[0].program_id]},  # exclude the first one
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        donors = response.json()["items"]

        # Calculate the number of unique programs
        programs = {donor["program_id"] for donor in donors}
        self.assertEqual(len(programs), 1)  # 1 program

        # Confirm the number of donors
        self.assertEqual(len(donors), 2)  # 2 donors

        # Calculate the total number of sample registrations
        sample_registrations = sum(
            len(donor["submitter_sample_ids"]) for donor in donors
        )
        self.assertEqual(sample_registrations, 16)  # 16 sample registrations

    def test_filter_primary_sites(self):
        """
        Test filtering donors by primary site.
        Verifies the correct count of primary site.

        Testing Strategy:
        - Extract the primary site from the first primary diagnosis.
        - Count the number of that primary site in the db
        - Send a valid request with a filter on the primary site.
        - Ensure that the count of returned matches the expected count.
        - Check each returned donor to confirm that it contains the specified primary site.
        """
        selected_primary_site = self.primary_diagnoses[0].primary_site

        # Calculate total count of the primary_site in all primary diagnoses
        primary_site_count = sum(
            1
            for pd in self.primary_diagnoses
            if selected_primary_site == pd.primary_site
        )

        response = self.client.get(
            self.donor_url,
            {"primary_site": [selected_primary_site]},
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        donors = response.json()["items"]

        # Calculate count of primary_site for returned donors
        response_primary_site_count = sum(
            1 for donor in donors if selected_primary_site in donor["primary_site"]
        )

        self.assertEqual(primary_site_count, response_primary_site_count)

        # Check each returned donor to confirm that it contains the specified primary site
        for donor in donors:
            self.assertIn(selected_primary_site, donor["primary_site"])

    def test_filter_treatment_type(self):
        """
        Test the filtering donors by treatment type.
        Verifies the correct count of treatment type from return donors,
        including repeated treatment types.

        Testing Strategy:
        - Extract treatment type from the first treatment.
        - Calculate the total count of the treatment type in all treatments.
        - Send a valid request with a filter on the treatment type.
        - Ensure that the count of treatment type for returned donors matches the expected count.
        """
        selected_treatment_type = self.treatments[0].treatment_type

        # Calculate total count of the treatment type in all treatments
        treatment_type_count = sum(
            1
            for treatment in self.treatments
            if selected_treatment_type in treatment.treatment_type
        )

        response = self.client.get(
            self.donor_url,
            {"treatment_type": [selected_treatment_type]},
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        donors = response.json()["items"]

        # Calculate count of treatment type for returned donors
        response_treatment_type_count = sum(
            1 for donor in donors if selected_treatment_type in donor["treatment_type"]
        )

        self.assertEqual(treatment_type_count, response_treatment_type_count)

    def test_filter_one_drug_name(self):
        """
        Test filtering donors by a drug name.
        Verifies the correct count of return donors.

        Testing Strategy:
        - Extract drug name from the first systemic therapy.
        - Collect distinct donors associated with the specified drug name.
        - Send a valid request with a filter on the drug name.
        - Ensure that the count of returned donors matches the expected count.
        """
        selected_drug_name = self.systemic_therapies[0].drug_name

        donors_with_selected_drug_name = {
            systemic_therapy.treatment_uuid.donor_uuid_id
            for systemic_therapy in self.systemic_therapies
            if systemic_therapy.drug_name == selected_drug_name
        }

        response = self.client.get(
            self.donor_url,
            {"systemic_therapy_drug_name": [selected_drug_name]},
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        donors = response.json()["items"]

        assert len(donors) == len(donors_with_selected_drug_name)

    def test_filter_two_drug_names(self):
        """
        Test filtering donors by 2 drug names.
        Verifies the correct count of return donors.

        Testing Strategy:
        - Extract 2 drug names from systemic therapies.
        - Collect donors associated with each drug name.
        - Send a valid request with a filter on both drug names.
        - Ensure that the count of returned donors matches the expected count.
        """
        selected_drug_names = [
            therapy.drug_name for therapy in self.systemic_therapies[:2]
        ]

        donors_with_selected_drug_names = set()
        for systemic_therapy in self.systemic_therapies:
            if systemic_therapy.drug_name in selected_drug_names:
                donors_with_selected_drug_names.add(
                    systemic_therapy.treatment_uuid.donor_uuid_id
                )

        response = self.client.get(
            self.donor_url,
            {"systemic_therapy_drug_name": selected_drug_names},
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        donors = response.json()["items"]

        assert len(donors) == len(donors_with_selected_drug_names)

    def test_donor_with_missing_data(self):
        """
        Test donor with missing data.
        Verifies that the API can still return the donor correctly.

        Testing Strategy:
        - Add a new donor without anything (e.g sample registrations or treatments)
        - Send a valid request with no filters.
        - Ensure that the response contains the donor with empty submitter_sample_ids and treatment_type.
        """

        DonorFactory.create(
            program_id=self.programs[0], submitter_donor_id="DONOR_MISSING_DATA"
        )

        response = self.client.get(
            self.donor_url,
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        missing_data_donor = next(
            (
                donor
                for donor in response.json()["items"]
                if donor["submitter_donor_id"] == "DONOR_MISSING_DATA"
            ),
            None,  # Default value if donor is not found
        )
        self.assertIsNotNone(
            missing_data_donor, "Donor with missing data not found in response"
        )
        self.assertIsNone(missing_data_donor["submitter_sample_ids"])
        self.assertEqual(missing_data_donor["treatment_type"], [])
