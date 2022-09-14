import uuid
import os

from rest_framework import status
from rest_framework.test import APITestCase

from chord_metadata_service.chord.data_types import DATA_TYPE_MCODEPACKET
from chord_metadata_service.chord.models import Project, Dataset, TableOwnership, Table
# noinspection PyProtectedMember
from chord_metadata_service.chord.ingest import (
    WORKFLOW_INGEST_FUNCTION_MAP,
    WORKFLOW_MCODE_JSON
)
from chord_metadata_service.chord.tests.constants import VALID_DATA_USE_1


EXAMPLE_INGEST_OUTPUTS_MCODE_JSON = {
    "json_document": os.path.join(os.path.dirname(__file__), "example_mcode_json.json"),
}


class GetMcodeApiTest(APITestCase):
    """
    Test that we can retrieve mcodepackets with valid dataset titles or without dataset title.
    """

    def setUp(self) -> None:
        """
        Set up 1 dataset and ingest 1 mcodepacket.
        """
        p = Project.objects.create(title="Project 1", description="")
        self.d = Dataset.objects.create(title="Dataset 1", description="Some dataset", data_use=VALID_DATA_USE_1,
                                        project=p)
        to = TableOwnership.objects.create(table_id=uuid.uuid4(), service_id=uuid.uuid4(), service_artifact="metadata",
                                           dataset=self.d)
        self.t = Table.objects.create(ownership_record=to, name="Table 1", data_type=DATA_TYPE_MCODEPACKET)

        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_MCODE_JSON](EXAMPLE_INGEST_OUTPUTS_MCODE_JSON, self.t.identifier)

    def test_get_mcodepackets(self):
        """
        Test that we can get 1 mcodepacket without a dataset title.
        """
        response = self.client.get('/api/mcodepackets')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 1)

    def test_get_mcodepackets_with_valid_dataset(self):
        """
        Test that we can get 1 mcodepacket with a valid dataset title.
        """
        response = self.client.get('/api/mcodepackets?datasets=Dataset+1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 1)

    def test_get_mcodepackets_with_invalid_dataset(self):
        """
        Test that we cannot get mcodepackets with invalid dataset titles.
        """
        response = self.client.get('/api/mcodepackets?datasets=notADataset')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 0)

    def test_get_mcodepackets_with_authz_dataset_1(self):
        """
        Test that we can get 1 mcodepacket with 1 authorized dataset.
        """
        response = self.client.get('/api/mcodepackets?authorized_datasets=Dataset+1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 1)

    def test_get_mcodepackets_with_authz_dataset_2(self):
        """
        Test that we can get 0 mcodepacket with 0 authorized dataset.
        """
        response = self.client.get('/api/mcodepackets?authorized_datasets=NO_DATASETS_AUTHORIZED')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 0)

    def test_get_mcodepackets_with_authz_dataset_3(self):
        """
        Test that we can get 0 phenopackets with 0 authorized datasets.
        """
        response = self.client.get('/api/mcodepackets?authorized_datasets=fakeDataset')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 0)
