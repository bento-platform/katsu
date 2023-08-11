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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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
