import json

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from chord_metadata_service.mohpackets.serializers import ProgramSerializer
from chord_metadata_service.mohpackets.tests.factories.program import ProgramFactory


class ProgramGETTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create test data using Factory Boy
        self.program_1 = ProgramFactory()
        
        # Define a custom authorized dataset for testing
        self.authorized_dataset = [
            {
                "username": "test_user",
                "datasets": [self.program_1.program_id],
            }
        ]
    
    def test_get_endpoint(self):
        with override_settings(LOCAL_AUTHORIZED_DATASET=self.authorized_dataset):
            # Set the Authorization header with value 'user2'
            authorization_header = 'test_user'
            url = '/v2/authorized/programs/'  # Replace with the correct URL

            # Issue a GET request to the endpoint with the Authorization header
            response = self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {authorization_header}')


            # Assert that the response status code is 200 OK
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Deserialize the response data and compare it with the test data
            expected_data = ProgramSerializer(self.program_1).data['program_id']
            self.assertEqual(response.data['results'][0]['program_id'], expected_data)