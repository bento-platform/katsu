from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from chord_metadata_service.mohpackets.serializers import *
from chord_metadata_service.mohpackets.tests.endpoints.factories import *


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.programs = ProgramFactory.create_batch(
            2,
        )
        cls.donors = DonorFactory.create_batch(
            4, program_id=factory.Iterator(cls.programs)
        )
        cls.primary_diagnoses = PrimaryDiagnosisFactory.create_batch(
            8, submitter_donor_id=factory.Iterator(cls.donors)
        )

        # Define a custom authorized dataset for testing
        cls.authorized_datasets = [
            {
                "username": "test_user_0",
                "is_allowed": False,
                "datasets": [],
            },
            {
                "username": "test_user_1",
                "is_allowed": False,
                "datasets": [cls.programs[0].program_id],
            },
            {
                "username": "test_user_2",
                "is_allowed": True,
                "datasets": [
                    cls.programs[0].program_id,
                    cls.programs[1].program_id,
                ],
            },
        ]

    def setUp(self):
        # Initialize the client before each test method
        self.client = APIClient()


class ProgramTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.get_url = "/v2/authorized/programs/"
        self.ingest_url = "/v2/ingest/programs"

    def test_valid_ingest(self):
        """
        Test that a valid list of program can be posted via the 'ingest/programs' endpoint
        and successfully creates the corresponding program objects in the database.
        Also add the new datasets to permissions
        """
        with override_settings(LOCAL_AUTHORIZED_DATASET=self.authorized_datasets):
            self.authorization_header = self.authorized_datasets[2]["username"]
            ingest_programs = ProgramFactory.build_batch(2)
            serialized_data = ProgramSerializer(ingest_programs, many=True).data
            response = self.client.post(
                self.ingest_url,
                data=serialized_data,
                format="json",
                HTTP_AUTHORIZATION=f"Bearer {self.authorization_header}",
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(
                Program.objects.count(), len(ingest_programs) + len(self.programs)
            )
            self.authorized_datasets[2]["datasets"].append(
                [program.program_id for program in ingest_programs]
            )

    def test_get_endpoint(self):
        """
        Test an authorized GET request and verifies that the response status code
        is 200 OK. It then compares the list of program IDs returned in the
        response with the program IDs fetched from the database.
        """
        with override_settings(LOCAL_AUTHORIZED_DATASET=self.authorized_datasets):
            self.authorization_header = self.authorized_datasets[2]["username"]
            # Issue a GET request to the endpoint with the Authorization header
            response = self.client.get(
                self.get_url,
                HTTP_AUTHORIZATION=f"Bearer {self.authorization_header}",
            )

            # Assert that the response status code is 200 OK
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Compare the response with the database
            expected_data = self.authorized_datasets[2]["datasets"]
            responsed_data = [
                item["program_id"] for item in response.data["results"]
            ]
            self.assertEqual(responsed_data, expected_data)


# class DonorTestCase(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         # Create test data using Factory Boy
#         self.donor = DonorFactory()
#         print("debug")

#     def test_with_several_news_content_by_one_user(self):
#         donors = DonorFactory.create_batch(
#                              5,
#                              program_id=self.program_1
#                         )


#     def test_dummy(self):
#         self.assertEqual(1 + 1, 2)

# class PrimaryDiagnosisTestCase(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         # Create test data using Factory Boy
#         self.donor = PrimaryDiagnosisFactory()
#         print("debug")
#     def test_dummy(self):
#         self.assertEqual(1 + 1, 2)
