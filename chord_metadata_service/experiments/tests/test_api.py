from jsonschema.validators import Draft7Validator

from django.test import TestCase
from chord_metadata_service.restapi.api_renderers import ExperimentCSVRenderer
import csv
import io

from rest_framework import status
from rest_framework.test import APITestCase
from chord_metadata_service.chord.models import Project, Dataset
from chord_metadata_service.chord.tests.constants import VALID_DATA_USE_1
from chord_metadata_service.chord.ingest import WORKFLOW_INGEST_FUNCTION_MAP
from chord_metadata_service.chord.workflows.metadata import WORKFLOW_PHENOPACKETS_JSON, WORKFLOW_EXPERIMENTS_JSON
from chord_metadata_service.restapi.tests.utils import load_local_json


EXAMPLE_INGEST_OUTPUTS_EXPERIMENTS_JSON = load_local_json("example_experiments.json")
EXAMPLE_INGEST_OUTPUTS_PHENOPACKETS_JSON = load_local_json("example_phenopackets.json")


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
        self.d1_id = self.d1.identifier
        self.d2 = Dataset.objects.create(title="dataset_2", description="Some dataset 2", data_use=VALID_DATA_USE_1,
                                         project=p)
        self.d2_id = self.d2.identifier
        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](EXAMPLE_INGEST_OUTPUTS_PHENOPACKETS_JSON, self.d1_id)
        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_EXPERIMENTS_JSON](EXAMPLE_INGEST_OUTPUTS_EXPERIMENTS_JSON, self.d1_id)

    def assert_response_200_and_length(self, response, assert_len: int):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["count"], assert_len)
        self.assertEqual(len(response_data["results"]), assert_len)

    def test_get_experiments(self):
        response = self.client.get('/api/experiments')
        self.assert_response_200_and_length(response, 2)

    def test_get_experiment_one(self):
        response = self.client.get('/api/experiments/katsu.experiment:1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data['id'], 'katsu.experiment:1')

    def test_get_experiment_schema(self):
        response = self.client.get('/api/experiment_schema')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        Draft7Validator.check_schema(response_data)

    def test_filter_experiments(self):
        response = self.client.get('/api/experiments?study_type=epigenetics')
        self.assert_response_200_and_length(response, 0)

    def test_filter_experiments_by_dataset_1(self):
        response = self.client.get(f'/api/experiments?datasets={self.d1_id}')
        self.assert_response_200_and_length(response, 2)

    def test_filter_experiments_by_dataset_2(self):
        response = self.client.get(f'/api/experiments?datasets={self.d2_id}')
        self.assert_response_200_and_length(response, 0)

    def test_filter_experiments_by_datasets_list(self):
        response = self.client.get(f'/api/experiments?datasets={self.d2_id},{self.d1_id}')
        self.assert_response_200_and_length(response, 2)

    def test_get_experiment_results(self):
        response = self.client.get('/api/experimentresults')
        self.assert_response_200_and_length(response, 4)

    def test_filter_experiment_results(self):
        response = self.client.get('/api/experimentresults?file_format=vcf')
        self.assert_response_200_and_length(response, 2)

    def test_filter_experiment_results_url(self):
        response = self.client.get('/api/experimentresults?url=example.org')
        self.assert_response_200_and_length(response, 1)

    def test_filter_experiment_results_indices(self):
        response = self.client.get('/api/experimentresults?indices=tabix')
        self.assert_response_200_and_length(response, 1)

    def test_filter_experiment_results_by_dataset_1(self):
        response = self.client.get(f'/api/experimentresults?datasets={self.d1_id}')
        self.assert_response_200_and_length(response, 4)

    def test_filter_experiment_results_by_dataset_2(self):
        response = self.client.get(f'/api/experimentresults?datasets={self.d2_id}')
        self.assert_response_200_and_length(response, 0)

    def test_filter_experiment_results_by_datasets_list(self):
        response = self.client.get(f'/api/experimentresults?datasets={self.d2_id},{self.d1_id}')
        self.assert_response_200_and_length(response, 4)

    def test_combine_filters_experiment_results(self):
        response = self.client.get(f'/api/experimentresults?datasets={self.d2_id},{self.d1_id}&file_format=cram')
        self.assert_response_200_and_length(response, 2)

    def test_combine_filters_experiment_results_2(self):
        # there are no experiments in dataset_2
        response = self.client.get(f'/api/experimentresults?datasets={self.d2_id}&file_format=vcf')
        self.assert_response_200_and_length(response, 0)

    def test_post_experiment_batch_no_data(self):
        response = self.client.post('/api/batch/experiments', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_post_experiment_batch_with_ids(self):
        response = self.client.post('/api/batch/experiments', {'id': ['katsu.experiment:1']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]['id'], 'katsu.experiment:1')


class TestExperimentCSVRenderer(TestCase):
    """
    Test the CSV renderer for the experiment API
    """
    def setUp(self):
        self.renderer = ExperimentCSVRenderer()
        self.data = [{
            'id': 'id1',
            'study_type': 'study_type1',
            'experiment_type': 'experiment_type1',
            'molecule': 'molecule1',
            'library_strategy': 'library_strategy1',
            'library_source': 'library_source1',
            'library_selection': 'library_selection1',
            'library_layout': 'library_layout1',
            'created': 'created1',
            'updated': 'updated1',
            'biosample': 'biosample1',
            'biosample_individual': {'id': 'individual_id1'},
        }]

    def test_csv_headers(self):
        response = self.renderer.render(self.data)
        csv_content = response.content.decode()
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        expected_headers = ['Id', 'Study type', 'Experiment type', 'Molecule', 'Library strategy',
                            'Library source', 'Library selection', 'Library layout',
                            'Created', 'Updated', 'Biosample', 'Individual id']
        self.assertListEqual(list(reader.fieldnames), expected_headers)

    def test_csv_render_with_missing_fields(self):
        data_with_missing_fields = [{
            'id': 'id3',
            'study_type': 'study_type3',
            'experiment_type': 'experiment_type3',
            'molecule': 'molecule3',
            'library_strategy': 'library_strategy3',
            'library_source': 'library_source3',
            # 'library_selection' intentionally missing
            'library_layout': 'library_layout3',
            'created': 'created3',
            'updated': 'updated3',
            'biosample': 'biosample3',
            'biosample_individual': {'id': 'individual_id3'},
        }]
        response = self.renderer.render(data_with_missing_fields)
        csv_content = response.content.decode()
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        row = next(reader)
        self.assertIsNone(row.get('library_selection'))

    def test_csv_render_with_empty_data(self):
        data_empty = [{}]
        response = self.renderer.render(data_empty)
        csv_content = response.content.decode()
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        row = next(reader)
        for row in reader:
            for key in row:
                self.assertEqual(row[key], '')
