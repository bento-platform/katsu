
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from chord_metadata_service.mohpackets.serializers import *
from chord_metadata_service.mohpackets.tests.endpoints.factories import *


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.program_1 = ProgramFactory()
        cls.donors = DonorFactory.create_batch(
            3, # number of instances
            program_id = cls.program_1
        )
        cls.primary_diagnosises = PrimaryDiagnosisFactory.create_batch(
            3, # number of instances
            submitter_donor_id = factory.Iterator(cls.donors)
        )
        
        # Define a custom authorized dataset for testing
        cls.authorized_dataset = [
            {
                "username": "test_user",
                "datasets": [cls.program_1.program_id],
            }
        ]

    def setUp(self):
        # Initialize the client before each test method
        self.client = APIClient()
        self.authorization_header = 'test_user'

class ProgramTestCase(BaseTestCase):
        
    def setUp(self):
        super().setUp()
        self.url = '/v2/authorized/programs/' 
        
    def test_dummy(self):
        print(self.donors[0].lost_to_followup_reason)
        self.assertEqual(1 + 1, 2)
    
    # def test_get_endpoint(self):
    #     with override_settings(LOCAL_AUTHORIZED_DATASET=self.authorized_dataset):
    #         # Issue a GET request to the endpoint with the Authorization header
    #         response = self.client.get(self.url, HTTP_AUTHORIZATION=f'Bearer {self.authorization_header}')

    #         # Assert that the response status code is 200 OK
    #         self.assertEqual(response.status_code, status.HTTP_200_OK)

    #         # Deserialize the response data and compare it with the test data
    #         expected_data = ProgramSerializer(self.program_1).data['program_id']
    #         self.assertEqual(response.data['results'][0]['program_id'], expected_data)

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