import csv
import io

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from chord_metadata_service.authz.tests.helpers import AuthzAPITestCase
from chord_metadata_service.chord.models import Project, Dataset
from chord_metadata_service.chord.ingest import WORKFLOW_INGEST_FUNCTION_MAP
from chord_metadata_service.chord.workflows.metadata import WORKFLOW_PHENOPACKETS_JSON
from chord_metadata_service.chord.tests.constants import VALID_DATA_USE_1
from chord_metadata_service.restapi.tests import constants as restapi_c

from . import constants as c
from ..schemas import PHENOPACKET_SCHEMA
from .. import models as m, serializers as s


class CreateBiosampleTest(AuthzAPITestCase):
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

        response = self.one_authz_post(reverse("biosamples-list"), json=self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.Biosample.objects.count(), 1)
        self.assertEqual(m.Biosample.objects.get().id, 'katsu.biosample_id:1')

    def test_create_biosample_forbidden(self):
        """ POST a new biosample. """

        response = self.one_no_authz_post(reverse("biosamples-list"), json=self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_invalid_biosample(self):
        """ POST a new biosample with invalid data. """

        invalid_response = self.one_authz_post(reverse('biosamples-list'), self.invalid_payload)
        self.assertEqual(
            invalid_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(m.Biosample.objects.count(), 0)

    def test_serializer_validate_invalid(self):
        serializer = s.BiosampleSerializer(data=self.invalid_payload)
        self.assertEqual(serializer.is_valid(), False)

    def test_serializer_validate_valid(self):
        serializer = s.BiosampleSerializer(data=self.valid_payload)
        self.assertEqual(serializer.is_valid(), True)

    def test_update(self):
        # Create initial biosample
        response = self.one_authz_post(reverse("biosamples-list"), json=self.valid_payload)
        biosample_id = response.data['id']

        # Should be 1
        initial_count = m.Biosample.objects.all().count()

        # Update the biosample.procedure.performed field
        self.valid_payload["procedure"]["performed"] = self.procedure_age_performed
        response = self.one_authz_put(f"/api/biosamples/{biosample_id}", json=self.valid_payload)

        # Should be 1 as well
        post_update_count = m.Biosample.objects.all().count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(initial_count, post_update_count)
        self.assertEqual(response.data['procedure']['performed'], self.procedure_age_performed)


class BatchBiosamplesCSVTest(AuthzAPITestCase):
    def setUp(self):
        self.individual = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.valid_payload = c.valid_biosample_1(self.individual)
        self.biosample = m.Biosample.objects.create(**self.valid_payload)
        self.view = 'batch/biosamples-list'
        self.post_biosamples_body = {
            'id': [str(self.biosample.id)],
            'format': 'csv'
        }

    def test_get_all_biosamples_batch(self):
        response = self.one_authz_get(reverse(self.view))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_all_biosamples_batch_forbidden(self):
        response = self.one_no_authz_get(reverse(self.view))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_biosamples_with_ids(self):
        response = self.one_authz_post(reverse(self.view), json=self.post_biosamples_body)
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

    def test_post_biosamples_with_ids_forbidden(self):
        response = self.one_no_authz_post(reverse(self.view), json=self.post_biosamples_body)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # TODO: fine-grain authz tests


class CreatePhenotypicFeatureTest(AuthzAPITestCase):

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

        response = self.one_authz_post(reverse("phenotypicfeatures-list"), json=self.valid_phenotypic_feature)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.PhenotypicFeature.objects.count(), 1)

    def test_create_phenotypic_feature_forbidden(self):
        """ POST a new phenotypic feature. """

        response = self.one_no_authz_post(reverse("phenotypicfeatures-list"), json=self.valid_phenotypic_feature)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(m.PhenotypicFeature.objects.count(), 0)

    def test_modifier(self):
        serializer = s.PhenotypicFeatureSerializer(data=self.invalid_phenotypic_feature)
        self.assertEqual(serializer.is_valid(), False)


class CreateDiseaseTest(AuthzAPITestCase):

    def setUp(self):
        self.disease = c.VALID_DISEASE_1
        self.invalid_disease = c.INVALID_DISEASE_2

    def test_create_disease(self):
        response = self.one_authz_post(reverse('diseases-list'), json=self.disease)
        serializer = s.DiseaseSerializer(data=self.disease)
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.Disease.objects.count(), 1)

    def test_create_disease_forbidden(self):
        response = self.one_no_authz_post(reverse('diseases-list'), json=self.disease)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(m.Disease.objects.count(), 0)

    def test_invalid_disease(self):
        serializer = s.DiseaseSerializer(data=self.invalid_disease)
        self.assertEqual(serializer.is_valid(), False)
        self.assertEqual(m.Disease.objects.count(), 0)


class CreateMetaDataTest(AuthzAPITestCase):

    def setUp(self):
        self.metadata = c.VALID_META_DATA_2

    def test_metadata(self):
        response = self.one_authz_post(reverse('metadata-list'), json=self.metadata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.MetaData.objects.count(), 1)

    def test_metadata_forbidden(self):
        response = self.one_no_authz_post(reverse('metadata-list'), json=self.metadata)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_serializer(self):
        # is_valid() calls validation on serializer
        serializer = s.MetaDataSerializer(data=self.metadata)
        self.assertEqual(serializer.is_valid(), True)


class CreatePhenopacketTest(AuthzAPITestCase):

    def setUp(self):
        individual = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.subject = individual.id
        meta = m.MetaData.objects.create(**c.VALID_META_DATA_2)
        self.metadata = meta.id
        self.phenopacket = c.valid_phenopacket(
            subject=self.subject,
            meta_data=self.metadata)

    def test_phenopacket_create(self):
        response = self.one_authz_post(reverse("phenopackets-list"), json=self.phenopacket)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.Phenopacket.objects.count(), 1)

    def test_phenopacket_create_forbidden(self):
        response = self.one_no_authz_post(reverse("phenopackets-list"), json=self.phenopacket)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(m.Phenopacket.objects.count(), 0)

    def test_serializer(self):
        serializer = s.PhenopacketSerializer(data=self.phenopacket)
        self.assertEqual(serializer.is_valid(), True)


class CreateGenomicInterpretationTest(AuthzAPITestCase):

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
        response = self.one_authz_post(reverse('genomicinterpretations-list'), json=self.genomic_interpretation_gene)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.GenomicInterpretation.objects.count(), 1)

    def test_genomic_interpretation_gene_forbidden(self):
        response = self.one_no_authz_post(reverse('genomicinterpretations-list'), json=self.genomic_interpretation_gene)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(m.GenomicInterpretation.objects.count(), 0)

    def test_genomic_interpretation_variant(self):
        response = self.one_authz_post(
            reverse('genomicinterpretations-list'), json=self.genomic_interpretation_variant)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.GenomicInterpretation.objects.count(), 1)

    def test_genomic_interpretation_variant_forbidden(self):
        response = self.one_no_authz_post(
            reverse('genomicinterpretations-list'), json=self.genomic_interpretation_variant)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(m.GenomicInterpretation.objects.count(), 0)

    def test_serializer(self):
        serializer = s.GenomicInterpretationSerializer(data=self.genomic_interpretation_gene)
        self.assertEqual(serializer.is_valid(), True)

        serializer = s.GenomicInterpretationSerializer(data=self.genomic_interpretation_variant)
        self.assertEqual(serializer.is_valid(), True)


class CreateDiagnosisTest(AuthzAPITestCase):

    def setUp(self):
        self.disease_ontology = c.VALID_DISEASE_ONTOLOGY
        self.diagnosis = c.valid_diagnosis(self.disease_ontology, "interpretation:unique_id")

    def test_diagnosis(self):
        response = self.one_authz_post(reverse('diagnoses-list'), json=self.diagnosis)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_diagnosis_forbidden(self):
        response = self.one_no_authz_post(reverse('diagnoses-list'), json=self.diagnosis)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_serializer(self):
        serializer = s.DiagnosisSerializer(data=self.diagnosis)
        self.assertEqual(serializer.is_valid(), True)


class CreateInterpretationTest(AuthzAPITestCase):

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

    def test_interpretation_create(self):
        response = self.one_authz_post(reverse('interpretations-list'), json=self.interpretation)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_interpretation_create_forbidden(self):
        response = self.one_no_authz_post(reverse('interpretations-list'), json=self.interpretation)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_interpretation_filter(self):
        # create interpretation with progress_status IN_PROGRESS
        self.one_authz_post(reverse('interpretations-list'), json=self.interpretation)

        request_url = reverse('interpretations-list')
        empty_response = self.one_authz_get(
            request_url,
            data={
                # Should return an empty list
                'progress_status': "COMPLETED"
            }
        )
        self.assertEqual(empty_response.data["count"], 0)

        valid_response = self.one_authz_get(
            request_url,
            data={
                # Should return a single Interpretation
                'progress_status': "IN_PROGRESS"
            }
        )
        self.assertEqual(valid_response.data["count"], 1)
        self.assertEqual(valid_response.data['results'][0]['id'], self.interpretation['id'])

        # forbidden get
        forbidden_response = self.one_no_authz_get(
            request_url,
            data={
                # Should return a single Interpretation
                'progress_status': "IN_PROGRESS"
            }
        )
        self.assertEqual(forbidden_response.status_code, status.HTTP_403_FORBIDDEN)


class GetPhenopacketsApiTest(AuthzAPITestCase):
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

    def test_get_phenopackets_no_access(self):
        """
        Test that we cannot get the complete set of phenopackets without authorization.
        """
        response = self.one_no_authz_get("/api/phenopackets")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_phenopackets(self):
        """
        Test that we can get 2 phenopackets without a dataset title.
        """
        response = self.one_authz_get("/api/phenopackets")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 2)

    def test_get_phenopackets_with_valid_dataset_via_scope(self):
        """
        Test that we can get 1 phenopacket under dataset_1 via discovery scoping.
        """
        response = self.one_authz_get(f"/api/phenopackets?dataset={self.d.identifier}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 1)

    def test_get_phenopackets_with_valid_dataset_via_scope_no_access(self):
        """
        Test that we can get 1 phenopacket under dataset_1 via discovery scoping.
        """
        response = self.one_no_authz_get(f"/api/phenopackets?dataset={self.d.identifier}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_phenopackets_with_valid_dataset_via_filter(self):
        """
        Test that we can get phenopackets under specific datasets via title using Django filter.
        """

        subtest_params = [
            ("dataset_1", 1),
            ("dataset_2", 1),
            ("dataset_1,dataset_2", 2),
            ("dataset_1,noSuchDataset", 1),
            ("notADataset", 0),
        ]

        for params in subtest_params:
            with self.subTest(params=params):
                ds_title, exp_count = params
                response = self.one_authz_get(f"/api/phenopackets?datasets={ds_title}")
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                response_data = response.json()
                self.assertEqual(len(response_data["results"]), exp_count)


class PhenopacketSchema(APITestCase):
    # No authz needed for these endpoints

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
