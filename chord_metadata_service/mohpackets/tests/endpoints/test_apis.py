from django.conf import settings
from django.test import TestCase, modify_settings, override_settings
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from chord_metadata_service.mohpackets.serializers import *
from chord_metadata_service.mohpackets.tests.endpoints.factories import *


class TestUser:
    def __init__(self, token, is_admin, datasets):
        self.token = token
        self.is_admin = is_admin
        self.datasets = datasets
        
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
        
        # Define test users with permission and datasets access
        cls.user_0 = TestUser(
            token="token_0",
            is_admin=False,
            datasets=[],
        )
        cls.user_1 = TestUser(
            token="token_1",
            is_admin=False,
            datasets=[cls.programs[0].program_id],
        )
        cls.user_2 = TestUser(
            token="token_2",
            is_admin=True,
            datasets=[cls.programs[0].program_id,cls.programs[1].program_id],
        )
        settings.LOCAL_AUTHORIZED_DATASET = [
            {
                "token": cls.user_0.token,
                "is_admin": cls.user_0.is_admin,
                "datasets": cls.user_0.datasets,
            },
            {
                "token": cls.user_1.token,
                "is_admin": cls.user_1.is_admin,
                "datasets": cls.user_1.datasets,
            },
              {
                "token": cls.user_2.token,
                "is_admin": cls.user_2.is_admin,
                "datasets": cls.user_2.datasets,
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


    def test_ingest_201_created(self):
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_ingest_403_unauthorized(self):
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

    def test_get_200_ok(self):
        """
        Test a successful GET request to the 'authorized/programs/' endpoint.

        Testing Strategy:
        - An authorized user (user_1) attempts a GET request for authorized programs.
        - The request should receive a 200 OK response.
        """
        response = self.client.get(
            self.get_url,
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
            "/v2/authorized/programs", 
            HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)
    
    def test_get_404_not_found(self):
        """
        Test a GET request for a 404 Not Found response.

        Testing Strategy:
        - Send a GET request to a non-existent endpoint ('/v2/authorized/programz').
        - The request should receive a 404 Not Found response.
        """
        response = self.client.get(
            "/v2/authorized/programz", 
            HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_get_datasets_match_permission(self):
        """
        Test that the response datasets match the authorized datasets for each user.

        Testing Strategy:
        - Verify that the response datasets match the datasets in the authorized dataset
          for each of the test users.
        """
        for user in [self.user_0, self.user_1, self.user_2]:
            response = self.client.get(
                self.get_url,
                HTTP_AUTHORIZATION=f"Bearer {user.token}",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            authorized_datasets = next(user_data['datasets'] for user_data in settings.LOCAL_AUTHORIZED_DATASET if user_data['token'] == user.token)
            response_datasets = [program['program_id'] for program in response.data['results']]
            self.assertEqual(response_datasets, authorized_datasets)

    # def test_get_endpoint(self):
    #     """
    #     Test an authorized GET request and verifies that the response status code
    #     is 200 OK. It then compares the list of program IDs returned in the
    #     response with the program IDs fetched from the database.
    #     """
    #     self.authorization_header = self.authorized_datasets[2]["username"]
    #     # Issue a GET request to the endpoint with the Authorization header
    #     response = self.client.get(
    #         self.get_url,
    #         HTTP_AUTHORIZATION=f"Bearer {self.authorization_header}",
    #     )

    #     # Assert that the response status code is 200 OK
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    #     # Compare the response with the database
    #     expected_data = self.authorized_datasets[2]["datasets"]
    #     responsed_data = [
    #         item["program_id"] for item in response.data["results"]
    #     ]
    #     self.assertEqual(responsed_data, expected_data)


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
