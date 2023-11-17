import csv
import io
import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
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
        self.assertEqual(m.Biosample.objects.get().id, 'biosample_id:1')

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
                       'individual age at collection',
                       'histological diagnosis', 'extra properties',
                       'created', 'updated', 'individual']:
            self.assertIn(column, [column_name.lower() for column_name in headers])


class CreatePhenotypicFeatureTest(APITestCase):

    def setUp(self):
        valid_payload = c.valid_phenotypic_feature()
        valid_payload.pop('pftype', None)
        valid_payload['type'] = {
            "id": "HP:0000520",
            "label": "Proptosis"
        }
        self.valid_phenotypic_feature = valid_payload
        invalid_payload = c.invalid_phenotypic_feature()
        invalid_payload['type'] = {
            "id": "HP:0000520",
            "label": "Proptosis"
        }
        self.invalid_phenotypic_feature = invalid_payload

    def test_create_phenotypic_feature(self):
        """ POST a new phenotypic feature. """

        response = get_post_response('phenotypicfeatures-list', self.valid_phenotypic_feature)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.PhenotypicFeature.objects.count(), 1)

    def test_modifier(self):
        serializer = s.PhenotypicFeatureSerializer(data=self.invalid_phenotypic_feature)
        self.assertEqual(serializer.is_valid(), False)


class CreateGeneTest(APITestCase):

    def setUp(self):
        self.gene = c.VALID_GENE_1
        self.duplicate_gene = c.DUPLICATE_GENE_2
        self.invalid_gene = c.INVALID_GENE_2

    def test_gene(self):
        response = get_post_response('genes-list', self.gene)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.Gene.objects.count(), 1)

    def test_alternate_ids(self):
        serializer = s.GeneSerializer(data=self.invalid_gene)
        self.assertEqual(serializer.is_valid(), False)


class CreateDiseaseTest(APITestCase):

    def setUp(self):
        self.disease = c.VALID_DISEASE_1
        self.invalid_disease = c.INVALID_DISEASE_2

    def test_disease(self):
        response = get_post_response('diseases-list', self.disease)
        serializer = s.DiseaseSerializer(data=self.disease)
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.Disease.objects.count(), 1)

    def test_invalid_disease(self):
        serializer = s.DiseaseSerializer(data=self.invalid_disease)
        self.assertEqual(serializer.is_valid(), False)
        self.assertEqual(m.Disease.objects.count(), 0)


class CreateMetaDataTest(APITestCase):

    def setUp(self):
        self.metadata = c.VALID_META_DATA_2

    def test_metadata(self):
        response = get_post_response('metadata-list', self.metadata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.MetaData.objects.count(), 1)

    def test_serializer(self):
        # is_valid() calls validation on serializer
        serializer = s.MetaDataSerializer(data=self.metadata)
        self.assertEqual(serializer.is_valid(), True)


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


class CreateGenomicInterpretationTest(APITestCase):

    def setUp(self):
        gene_description = m.GeneDescriptor.objects.create(**c.VALID_GENE_DESCRIPTOR_1)
        self.genomic_interpretation_gene = c.valid_genomic_interpretation(gene_descriptor=gene_description.value_id)

        variant_descriptor = m.VariationDescriptor.objects.create(
            **c.valid_variant_descriptor(gene_description))
        variant_interpretation = m.VariantInterpretation.objects.create(
            **c.valid_variant_interpretation(variant_descriptor=variant_descriptor)
        )
        self.genomic_interpretation_variant = c.valid_genomic_interpretation(
            variant_interpretation=variant_interpretation.id)

    def test_genomic_interpretation_gene(self):
        response = get_post_response('genomicinterpretations-list', self.genomic_interpretation_gene)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.GenomicInterpretation.objects.count(), 1)

    def test_genomic_interpretation_variant(self):
        response = get_post_response('genomicinterpretations-list', self.genomic_interpretation_variant)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.GenomicInterpretation.objects.count(), 1)

    def test_serializer(self):
        serializer = s.GenomicInterpretationSerializer(data=self.genomic_interpretation_gene)
        self.assertEqual(serializer.is_valid(), True)

        serializer = s.GenomicInterpretationSerializer(data=self.genomic_interpretation_variant)
        self.assertEqual(serializer.is_valid(), True)


class CreateDiagnosisTest(APITestCase):

    def setUp(self):
        self.disease_ontology = c.VALID_DISEASE_ONTOLOGY
        self.diagnosis = c.valid_diagnosis(self.disease_ontology)

    def test_diagnosis(self):
        response = get_post_response('diagnoses-list', self.diagnosis)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        serializer = s.DiagnosisSerializer(data=self.diagnosis)
        self.assertEqual(serializer.is_valid(), True)


class CreateInterpretationTest(APITestCase):

    def setUp(self):
        self.individual = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.metadata = m.MetaData.objects.create(**c.VALID_META_DATA_2)
        self.phenopacket = m.Phenopacket.objects.create(**c.valid_phenopacket(
            subject=self.individual,
            meta_data=self.metadata)
        ).id
        self.metadata_interpretation = m.MetaData.objects.create(**c.VALID_META_DATA_2).id
        self.disease_ontology = c.VALID_DISEASE_ONTOLOGY
        self.diagnosis = m.Diagnosis.objects.create(**c.valid_diagnosis(self.disease_ontology)).id
        self.interpretation = c.valid_interpretation(diagnosis=self.diagnosis)

    def test_interpretation_list(self):
        response = get_post_response('interpretations-list', self.interpretation)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_interpretation_filter(self):
        # create interpretation with progress_status IN_PROGRESS
        _ = get_post_response('interpretations-list', self.interpretation)

        request_url = reverse('interpretations-list')
        empty_response = self.client.get(
            request_url,
            data={
                # Should return an empty list
                'progress_status': "COMPLETED"
            }
        )
        self.assertEqual(empty_response.data["count"], 0)

        valid_response = self.client.get(
            request_url,
            data={
                # Should return a single Interpretation
                'progress_status': "IN_PROGRESS"
            }
        )
        self.assertEqual(valid_response.data["count"], 1)
        self.assertEqual(valid_response.data['results'][0]['id'], self.interpretation['id'])


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
