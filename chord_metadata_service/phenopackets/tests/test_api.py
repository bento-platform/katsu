import csv
import io
import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from chord_metadata_service.phenopackets.schemas import PHENOPACKET_SCHEMA
from . import constants as c
from .. import models as m, serializers as s

from chord_metadata_service.restapi.tests.utils import get_post_response
from chord_metadata_service.chord.models import Project, Dataset
from chord_metadata_service.chord.ingest import WORKFLOW_INGEST_FUNCTION_MAP
from chord_metadata_service.chord.workflows.metadata import WORKFLOW_PHENOPACKETS_JSON
from chord_metadata_service.chord.tests.constants import VALID_DATA_USE_1
from chord_metadata_service.restapi.tests import constants as restapi_c


class CreateBiosampleTest(APITestCase):
    """ Test module for creating an Biosample. """

    def setUp(self):
        self.individual = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.procedure = c.VALID_PROCEDURE_1
        self.valid_payload = c.valid_biosample_1(self.individual.id, self.procedure)
        self.invalid_payload = {
            "id": "biosample:1",
            "individual": self.individual.id,
            "procedure": self.procedure,
            "description": "This is a test description.",
            "sampled_tissue": {
                "id": "UBERON_0001256"
            },
            "histological_diagnosis": {
                "id": "NCIT:C39853",
                "label": "Infiltrating Urothelial Carcinoma"
            },
            "tumor_progression": {
                "id": "NCIT:C84509",
                "label": "Primary Malignant Neoplasm"
            },
            "tumor_grade": {
                "id": "NCIT:C48766",
                "label": "pT2b Stage Finding"
            },
            "diagnostic_markers": [
                {
                    "id": "NCIT:C49286",
                    "label": "Hematology Test"
                },
                {
                    "id": "NCIT:C15709",
                    "label": "Genetic Testing"
                }
            ]
        }
        self.procedure_age_performed = {
            "age": {
                "iso_8601_duration": "P25Y"
            }
        }

    def test_create_biosample(self):
        """ POST a new biosample. """

        response = get_post_response('biosamples-list', self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.Biosample.objects.count(), 1)
        self.assertEqual(m.Biosample.objects.get().id, 'katsu.biosample_id:1')

    def test_create_invalid_biosample(self):
        """ POST a new biosample with invalid data. """

        invalid_response = get_post_response('biosamples-list', self.invalid_payload)
        self.assertEqual(
            invalid_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(m.Biosample.objects.count(), 0)

    def test_seriliazer_validate_invalid(self):
        serializer = s.BiosampleSerializer(data=self.invalid_payload)
        self.assertEqual(serializer.is_valid(), False)

    def test_seriliazer_validate_valid(self):
        serializer = s.BiosampleSerializer(data=self.valid_payload)
        self.assertEqual(serializer.is_valid(), True)

    def test_update(self):
        # Create initial biosample
        response = get_post_response('biosamples-list', self.valid_payload)
        biosample_id = response.data['id']

        # Should be 1
        initial_count = m.Biosample.objects.all().count()

        # Update the biosample.procedure.performed field
        self.valid_payload["procedure"]["performed"] = self.procedure_age_performed
        # response = get_post_response('biosamples-list', self.valid_payload)
        response = self.client.put(
            f"/api/biosamples/{biosample_id}",
            data=json.dumps(self.valid_payload),
            content_type='application/json',
        )

        # Should be 1 as well
        post_update_count = m.Biosample.objects.all().count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(initial_count, post_update_count)
        self.assertEqual(response.data['procedure']['performed'], self.procedure_age_performed)


class BatchBiosamplesCSVTest(APITestCase):
    def setUp(self):
        self.individual = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.valid_payload = c.valid_biosample_1(self.individual)
        self.biosample = m.Biosample.objects.create(**self.valid_payload)
        self.view = 'batch/biosamples-list'

    def test_get_all_biosamples(self):
        response = self.client.get(reverse(self.view))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1),

    def test_post_biosamples_with_ids(self):
        data = {
            'id': [str(self.biosample.id)],
            'format': 'csv'
        }
        response = get_post_response(self.view, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        content = response.content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        body = list(csv_reader)
        headers = body.pop(0)
        for column in ['id', 'description', 'sampled tissue',
                       'time of collection',
                       'histological diagnosis', 'extra properties',
                       'created', 'updated', 'individual']:
            self.assertIn(column, [column_name.lower() for column_name in headers])


class CreatePhenopacketTest(APITestCase):

    def setUp(self):
        individual = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.subject = individual.id
        meta = m.MetaData.objects.create(**c.VALID_META_DATA_2)
        self.metadata = meta.id
        self.phenopacket = c.valid_phenopacket(
            subject=self.subject,
            meta_data=self.metadata)

    def test_phenopacket(self):
        response = get_post_response('phenopackets-list', self.phenopacket)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.Phenopacket.objects.count(), 1)

    def test_serializer(self):
        serializer = s.PhenopacketSerializer(data=self.phenopacket)
        self.assertEqual(serializer.is_valid(), True)


class GetPhenopacketsApiTest(APITestCase):
    """
    Test that we can retrieve phenopackets with valid dataset titles or without dataset title.
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
            restapi_c.VALID_PHENOPACKET_1, self.d.identifier)
        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](
            restapi_c.VALID_PHENOPACKET_2, self.d2.identifier)

    def test_get_phenopackets(self):
        """
        Test that we can get 2 phenopackets without a dataset title.
        """
        response = self.client.get('/api/phenopackets')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 2)

    def test_get_phenopackets_with_valid_dataset(self):
        """
        Test that we can get 1 phenopacket under dataset_1.
        """
        response = self.client.get('/api/phenopackets?datasets=dataset_1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 1)

    def test_get_phenopackets_with_valid_dataset_2(self):
        """
        Test that we can get 1 phenopacket under dataset_2.
        """
        response = self.client.get('/api/phenopackets?datasets=dataset_2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 1)

    def test_get_phenopackets_with_valid_dataset_3(self):
        """
        Test that we can get 2 phenopackets under both dataset_1 and dataset_2.
        """
        response = self.client.get('/api/phenopackets?datasets=dataset_1,dataset_2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 2)

    def test_get_phenopackets_with_valid_dataset_4(self):
        """
        Test that we can get 1 phenopacket under dataset_1 and an invalid dataset.
        """
        response = self.client.get('/api/phenopackets?datasets=dataset_1,noSuchDataset')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 1)

    def test_get_phenopackets_with_invalid_dataset(self):
        """
        Test that we cannot get phenopackets with invalid dataset titles.
        """
        response = self.client.get('/api/phenopackets?datasets=notADataset')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 0)

    def test_get_phenopackets_with_authz_dataset_1(self):
        """
        Test that we cannot get phenopackets with no authorized datasets.
        """
        response = self.client.get('/api/phenopackets?datasets=dataset_1&authorized_datasets=dataset2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 0)

    def test_get_phenopackets_with_authz_dataset_2(self):
        """
        Test that we can get 1 phenopacket with 1 authorized datasets.
        """
        response = self.client.get('/api/phenopackets?authorized_datasets=dataset_1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 1)

    def test_get_phenopackets_with_authz_dataset_3(self):
        """
        Test that we can get 2 phenopackets with 2 authorized datasets.
        """
        response = self.client.get('/api/phenopackets?authorized_datasets=dataset_1,dataset_2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 2)

    def test_get_phenopackets_with_authz_dataset_4(self):
        """
        Test that we can get 1 phenopackets with 1 authorized datasets.
        """
        response = self.client.get('/api/phenopackets?datasets=dataset_1&authorized_datasets=dataset_1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 1)

    def test_get_phenopackets_with_authz_dataset_5(self):
        """
        Test that we can get 0 phenopackets with 0 authorized datasets.
        """
        response = self.client.get('/api/phenopackets?authorized_datasets=NO_DATASETS_AUTHORIZED')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 0)


class PhenopacketSchema(APITestCase):

    def test_get_phenopacket_schema(self):
        response = self.client.get("/api/schemas/phenopacket")
        schema = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(schema, PHENOPACKET_SCHEMA)

    def test_get_pheno_subschemas(self):
        for subschema in PHENOPACKET_SCHEMA["properties"].values():
            prop_key = subschema["$id"].split('/')[-1]
            response = self.client.get(reverse("chord-phenopacket-subschema", kwargs={"subschema": prop_key}))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json(), subschema)
