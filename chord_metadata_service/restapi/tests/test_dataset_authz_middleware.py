import os
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import modify_settings

from chord_metadata_service.chord.models import Project, Dataset
from chord_metadata_service.chord.ingest import WORKFLOW_INGEST_FUNCTION_MAP
from chord_metadata_service.chord.workflows.metadata import WORKFLOW_PHENOPACKETS_JSON
from chord_metadata_service.chord.tests.constants import VALID_DATA_USE_1
from chord_metadata_service.restapi.tests import constants as c

import logging

logging.getLogger().setLevel(logging.INFO)

EXAMPLE_INGEST_OUTPUTS_PHENOPACKETS_JSON_1 = {
    "json_document": os.path.join(os.path.dirname(__file__), "example_phenopackets_1.json"),
}

EXAMPLE_INGEST_OUTPUTS_PHENOPACKETS_JSON_2 = {
    "json_document": os.path.join(os.path.dirname(__file__), "example_phenopackets_2.json"),
}

# modify_settings makes sure CANDIG settings is enabled on GitHub Actions


@modify_settings(MIDDLEWARE={
    'append': 'chord_metadata_service.restapi.preflight_req_middleware.PreflightRequestMiddleware',
    'prepend': 'chord_metadata_service.restapi.candig_authz_middleware.CandigAuthzMiddleware',
})
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

        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](
            c.VALID_PHENOPACKET_1, self.d.identifier)
        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](
            c.VALID_PHENOPACKET_2, self.d2.identifier)

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
        Test that the /api/datasets returns 200 with 1 project even if OPA is malconfigured,
        as this endpoint is not covered under the middleware.
        """
        response = self.client.get('/api/projects')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 1)

    @override_settings(CANDIG_AUTHORIZATION='OPA', CANDIG_OPA_URL='0.0.0.0', CACHE_TIME=0)
    def test_get_phenopackets_with_invalid_OPA_config_3(self):
        """
        Test that the server returns 403 for /api/phenopackets if the OPA Server cannot be reached.
        """
        response = self.client.get('/api/phenopackets')
        self.assertEqual(response.status_code, 403)
