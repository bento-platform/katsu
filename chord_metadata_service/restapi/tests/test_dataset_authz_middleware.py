import uuid
import os
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET
from chord_metadata_service.chord.models import Project, Dataset, TableOwnership, Table
# noinspection PyProtectedMember
from chord_metadata_service.chord.ingest import (
    WORKFLOW_INGEST_FUNCTION_MAP,
    WORKFLOW_PHENOPACKETS_JSON
)
from chord_metadata_service.chord.tests.constants import VALID_DATA_USE_1

EXAMPLE_INGEST_OUTPUTS_PHENOPACKETS_JSON_1 = {
    "json_document": os.path.join(os.path.dirname(__file__), "example_phenopackets_1.json"),
}

EXAMPLE_INGEST_OUTPUTS_PHENOPACKETS_JSON_2 = {
    "json_document": os.path.join(os.path.dirname(__file__), "example_phenopackets_2.json"),
}


class GetPhenopacketsWithOpaTest(APITestCase):
    """
    Test that we can retrieve phenopackets when OPA is not configured, and that we cannot retrieve
    phenopackets when OPA is not correctly configured.
    """

    def setUp(self) -> None:
        """
        Create two datasets and ingest 1 phenopacket into each.
        """
        p = Project.objects.create(title="Project 1", description="")
        self.d = Dataset.objects.create(title="dataset_1", description="Some dataset", data_use=VALID_DATA_USE_1,
                                        project=p)
        self.d2 = Dataset.objects.create(title="dataset_2", description="Some dataset", data_use=VALID_DATA_USE_1,
                                         project=p)
        to = TableOwnership.objects.create(table_id=uuid.uuid4(), service_id=uuid.uuid4(), service_artifact="metadata",
                                           dataset=self.d)
        to2 = TableOwnership.objects.create(table_id=uuid.uuid4(), service_id=uuid.uuid4(), service_artifact="metadata",
                                            dataset=self.d2)
        self.t = Table.objects.create(ownership_record=to, name="Table 1", data_type=DATA_TYPE_PHENOPACKET)
        self.t2 = Table.objects.create(ownership_record=to2, name="Table 2", data_type=DATA_TYPE_PHENOPACKET)

        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](
            EXAMPLE_INGEST_OUTPUTS_PHENOPACKETS_JSON_1, self.t.identifier)
        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](
            EXAMPLE_INGEST_OUTPUTS_PHENOPACKETS_JSON_2, self.t2.identifier)

    def test_get_phenopackets(self):
        """
        Test that we can get 2 phenopackets without OPA enabled (default).
        """
        response = self.client.get('/api/phenopackets')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 2)

    @override_settings(CANDIG_AUTHORIZATION='OPA')
    def test_get_phenopackets_with_invalid_OPA_config(self):
        """
        Test that the server returns 403 if cache is not disabled when OPA is enabled.
        """
        response = self.client.get('/api/phenopackets')
        self.assertEqual(response.status_code, 403)

    @override_settings(CANDIG_AUTHORIZATION='OPA')
    def test_get_phenopackets_with_invalid_OPA_config_2(self):
        """
        Test that the /api/datasets returns 200 with 2 datasets even if OPA is malconfigured,
        as this endpoint is not covered under the middleware.
        """
        response = self.client.get('/api/datasets')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 2)

    @override_settings(CANDIG_AUTHORIZATION='OPA')
    def test_get_phenopackets_with_invalid_OPA_config_3(self):
        """
        Test that the /api/datasets returns 200 with 1 project even if OPA is malconfigured,
        as this endpoint is not covered under the middleware.
        """
        response = self.client.get('/api/projects')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 1)

    @override_settings(CANDIG_AUTHORIZATION='OPA', CANDIG_OPA_URL='0.0.0.0', CACHE_TIME=0)
    def test_get_phenopackets_with_invalid_OPA_config_4(self):
        """
        Test that the server returns 403 for /api/phenopackets if the OPA Server cannot be reached.
        """
        response = self.client.get('/api/phenopackets')
        self.assertEqual(response.status_code, 403)
