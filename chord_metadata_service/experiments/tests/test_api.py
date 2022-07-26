import os
from uuid import uuid4

from rest_framework import status
from rest_framework.test import APITestCase
from chord_metadata_service.chord.models import Project, Dataset, TableOwnership, Table
from chord_metadata_service.chord.tests.constants import VALID_DATA_USE_1
from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.chord.ingest import (
    WORKFLOW_INGEST_FUNCTION_MAP,
    WORKFLOW_PHENOPACKETS_JSON,
    WORKFLOW_EXPERIMENTS_JSON,
)


EXAMPLE_INGEST_OUTPUTS_PHENOPACKETS_JSON = {
    "json_document": os.path.join(os.path.dirname(__file__), "example_phenopackets.json"),
}

EXAMPLE_INGEST_OUTPUTS_EXPERIMENTS_JSON = {
    "json_document": os.path.join(os.path.dirname(__file__), "example_experiments.json"),
}


class GetExperimentsAppApisTest(APITestCase):
    """
    Test Experiments app APIs.
    """

    def setUp(self) -> None:
        """
        Create two datasets but ingest phenopackets and experiments in just one dataset
        """
        p = Project.objects.create(title="Test Project", description="Test")
        self.d1 = Dataset.objects.create(title="dataset_1", description="Some dataset 1", data_use=VALID_DATA_USE_1,
                                         project=p)
        self.d2 = Dataset.objects.create(title="dataset_2", description="Some dataset 2", data_use=VALID_DATA_USE_1,
                                         project=p)
        to1 = TableOwnership.objects.create(table_id=uuid4(), service_id=uuid4(), service_artifact="metadata",
                                            dataset=self.d1)
        to2 = TableOwnership.objects.create(table_id=uuid4(), service_id=uuid4(), service_artifact="metadata",
                                            dataset=self.d1)
        self.t1 = Table.objects.create(ownership_record=to1, name="Table 1", data_type=DATA_TYPE_PHENOPACKET)
        self.t2 = Table.objects.create(ownership_record=to2, name="Table 2", data_type=DATA_TYPE_EXPERIMENT)
        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](
            EXAMPLE_INGEST_OUTPUTS_PHENOPACKETS_JSON, self.t1.identifier)
        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_EXPERIMENTS_JSON](
            EXAMPLE_INGEST_OUTPUTS_EXPERIMENTS_JSON, self.t2.identifier)

    def test_get_experiments(self):
        response = self.client.get('/api/experiments')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["count"], 2)
        self.assertEqual(len(response_data["results"]), 2)

    def test_filter_experiments(self):
        response = self.client.get('/api/experiments?study_type=epigenetics')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["count"], 0)
        self.assertEqual(len(response_data["results"]), 0)

    def test_filter_experiments_by_dataset_1(self):
        response = self.client.get('/api/experiments?datasets=dataset_1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["count"], 2)
        self.assertEqual(len(response_data["results"]), 2)

    def test_filter_experiments_by_dataset_2(self):
        response = self.client.get('/api/experiments?datasets=dataset_2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["count"], 0)
        self.assertEqual(len(response_data["results"]), 0)

    def test_filter_experiments_by_datasets_list(self):
        response = self.client.get('/api/experiments?datasets=dataset_2,dataset_1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["count"], 2)
        self.assertEqual(len(response_data["results"]), 2)

    def test_get_experiment_results(self):
        response = self.client.get('/api/experimentresults')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["count"], 4)
        self.assertEqual(len(response_data["results"]), 4)

    def test_filter_experiment_results(self):
        response = self.client.get('/api/experimentresults?file_format=vcf')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["count"], 2)
        self.assertEqual(len(response_data["results"]), 2)

    def test_filter_experiment_results_by_dataset_1(self):
        response = self.client.get('/api/experimentresults?datasets=dataset_1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["count"], 4)
        self.assertEqual(len(response_data["results"]), 4)

    def test_filter_experiment_results_by_dataset_2(self):
        response = self.client.get('/api/experimentresults?datasets=dataset_2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["count"], 0)
        self.assertEqual(len(response_data["results"]), 0)

    def test_filter_experiment_results_by_datasets_list(self):
        response = self.client.get('/api/experimentresults?datasets=dataset_2,dataset_1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["count"], 4)
        self.assertEqual(len(response_data["results"]), 4)

    def test_combine_filters_experiment_results(self):
        response = self.client.get('/api/experimentresults?datasets=dataset_2,dataset_1&file_format=cram')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["count"], 2)
        self.assertEqual(len(response_data["results"]), 2)

    def test_combine_filters_experiment_results_2(self):
        # there are no experiments in dataset_2
        response = self.client.get('/api/experimentresults?datasets=dataset_2&file_format=vcf')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["count"], 0)
        self.assertEqual(len(response_data["results"]), 0)
