import factory
from django.conf import settings
from rest_framework import status

from chord_metadata_service.mohpackets.models import Chemotherapy
from chord_metadata_service.mohpackets.serializers import ChemotherapySerializer
from chord_metadata_service.mohpackets.tests.endpoints.base import BaseTestCase
from chord_metadata_service.mohpackets.tests.endpoints.factories import (
    ChemotherapyFactory,
)


# INGEST API
# ----------
class IngestTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.chemotherapy_url = "/v2/ingest/chemotherapies/"

    def test_chemotherapy_create_authorized(self):
        """
        Test that an admin user can create a chemotherapy record and receive 201 Created response.

        Testing Strategy:
        - Build Chemotherapy data based on the existing primary_diagnosis_id
        - An authorized user (user_2) with admin permission.
        - User can perform a POST request for chemotherapy record creation.
        """
        chemotherapy_data = ChemotherapyFactory.build_batch(
            submitter_treatment_id=factory.Iterator(self.treatments),
            size=2,
        )
        serialized_data = ChemotherapySerializer(chemotherapy_data, many=True).data
        response = self.client.post(
            self.chemotherapy_url,
            data=serialized_data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.user_2.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_chemotherapy_create_unauthorized(self):
        """
        Test that a non-admin user attempting to create a chemotherapy record receives a 403 Forbidden response.

        Testing Strategy:
        - Build Chemotherapy data based on the existing primary_diagnosis_id
        - An unauthorized user (user_0) with no permission.
        - User cannot perform a POST request for chemotherapy record creation.
        """
        chemotherapy_data = ChemotherapyFactory.build_batch(
            submitter_treatment_id=factory.Iterator(self.treatments),
            size=2,
        )
        serialized_data = ChemotherapySerializer(chemotherapy_data, many=True).data
        response = self.client.post(
            self.chemotherapy_url,
            data=serialized_data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.user_0.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
