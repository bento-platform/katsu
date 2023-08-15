import factory
from django.conf import settings
from rest_framework import status

from chord_metadata_service.mohpackets.models import FollowUp
from chord_metadata_service.mohpackets.serializers import FollowUpSerializer
from chord_metadata_service.mohpackets.tests.endpoints.base import BaseTestCase
from chord_metadata_service.mohpackets.tests.endpoints.factories import FollowUpFactory


# INGEST API
# ----------
class IngestTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.follow_up_url = "/v2/ingest/follow_ups/"

    def test_follow_up_create_authorized(self):
        """
        Test that an admin user can create a follow-up and receive 201 Created response.

        Testing Strategy:
        - Build FollowUp data based on the existing primary_diagnosis_id
        - An authorized user (user_2) with admin permission.
        - User can perform a POST request for follow-up creation.
        """
        follow_up_data = FollowUpFactory.build_batch(
            submitter_treatment_id=factory.Iterator(self.treatments),
            size=2,
        )
        serialized_data = FollowUpSerializer(follow_up_data, many=True).data
        response = self.client.post(
            self.follow_up_url,
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

    def test_follow_up_create_unauthorized(self):
        """
        Test that a non-admin user attempting to create a follow-up receives a 403 Forbidden response.

        Testing Strategy:
        - Build FollowUp data based on the existing primary_diagnosis_id
        - An unauthorized user (user_0) with no permission.
        - User cannot perform a POST request for follow-up creation.
        """
        follow_up_data = FollowUpFactory.build_batch(
            submitter_treatment_id=factory.Iterator(self.treatments),
            size=2,
        )
        serialized_data = FollowUpSerializer(follow_up_data, many=True).data
        response = self.client.post(
            self.follow_up_url,
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
        self.follow_ups_url = "/v2/authorized/follow_ups/"

    def test_get_follow_ups_200_ok(self):
        """
        Test a successful GET request to the 'authorized/follow_ups/' endpoint.

        Testing Strategy:
        - An authorized user (user_1) attempts a GET request for authorized follow-ups.
        - The request should receive a 200 OK response.
        """
        response = self.client.get(
            self.follow_ups_url,
            HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_follow_ups_301_redirect(self):
        """
        Test a GET request endpoint with a 301 redirection.

        Testing Strategy:
        - Send a GET request to the '/v2/authorized/follow_ups' endpoint.
        - The request should receive a 301 redirection response.
        """
        response = self.client.get(
            "/v2/authorized/follow_ups",
            HTTP_AUTHORIZATION=f"Bearer {self.user_1.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)


# OTHERS
# ------
class OthersTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.follow_ups_url = "/v2/authorized/follow_ups/"

    def test_get_datasets_match_permission(self):
        """
        Test that the response datasets match the authorized datasets for each user.

        Testing Strategy:
        - Get a list of datasets associated with follow-ups of each user
        - Call the endpoint to get all follow-ups
        - Verify that the response datasets match the datasets in the authorized datasets
          for each of the test users.
        """
        for user in self.users:
            authorized_datasets = next(
                user_data["datasets"]
                for user_data in settings.LOCAL_AUTHORIZED_DATASET
                if user_data["token"] == user.token
            )
            # get follow-ups' datasets from the database
            expected_datasets = list(
                FollowUp.objects.filter(program_id__in=authorized_datasets).values_list(
                    "submitter_follow_up_id", flat=True
                )
            )

            # get follow-ups' datasets from the API
            response = self.client.get(
                self.follow_ups_url,
                HTTP_AUTHORIZATION=f"Bearer {user.token}",
            )
            response_data = [
                follow_up["submitter_follow_up_id"]
                for follow_up in response.data["results"]
            ]

            self.assertEqual(response_data, expected_datasets)

    def test_post_request_405(self):
        """
        Test a POST request to the '/authorized/follow-ups/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.post(
            self.follow_ups_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_request_405(self):
        """
        Test a PUT request to the '/authorized/follow-ups/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.put(
            self.follow_ups_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_request_405(self):
        """
        Test a PATCH request to the '/authorized/follow-ups/' endpoint.
        The request should receive a 405 Method Not Allowed response.
        """
        response = self.client.patch(
            self.follow_ups_url, HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_request_404(self):
        """
        Test a DELETE request 'authorized/follow_ups/{id}/' endpoint.

        Testing Strategy:
        - Create a new follow-up to delete
        - The request should receive a 404 response.
        """
        follow_up_to_delete = FollowUpFactory()
        response = self.client.delete(
            f"{self.follow_ups_url}{follow_up_to_delete.submitter_follow_up_id}/",
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
