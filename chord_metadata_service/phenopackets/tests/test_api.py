import json
from django.urls import include, path, reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import *
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS
from .constants import *
from ..serializers import *


class CreateBiosampleTest(APITestCase):
	""" Test module for creating an Biosample. """

	def setUp(self):
		self.individual = Individual.objects.create(**VALID_INDIVIDUAL_1)
		self.procedure = VALID_PROCEDURE_1
		self.valid_payload = {
			"id": "biosample:1",
			"individual": self.individual.id,
			"procedure": self.procedure,
			"description": "This is a test description.",
			"sampled_tissue": {
				"id": "UBERON_0001256",
				"label": "wall of urinary bladder"
			},
			"individual_age_at_collection": "P67Y3M2D",
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
		self.invalid_payload = {
			"id": "biosample:1",
			"individual": self.individual.id,
			"procedure": self.procedure,
			"description": "This is a test description.",
			"sampled_tissue": {
				"id": "UBERON_0001256"
			},
			"individual_age_at_collection": "P67Y3M2D",
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

	def test_create_biosample(self):
		""" POST a new biosample. """

		response = self.client.post(
			reverse('biosample-list'),
			data=json.dumps(self.valid_payload),
			content_type='application/json'
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Biosample.objects.count(), 1)
		self.assertEqual(Biosample.objects.get().id, 'biosample:1')

	def test_create_invalid_biosample(self):
		""" POST a new biosample with invalid data. """

		invalid_response = self.client.post(
			reverse('biosample-list'),
			data=json.dumps(self.invalid_payload),
			content_type='application/json'
		)
		self.assertEqual(
			invalid_response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(Biosample.objects.count(), 0)

	def test_seriliazer_validate_invalid(self):
		serializer = BiosampleSerializer(data=self.invalid_payload)
		self.assertEqual(serializer.is_valid(), False)

	def test_seriliazer_validate_valid(self):
		serializer = BiosampleSerializer(data=self.valid_payload)
		self.assertEqual(serializer.is_valid(), True)


class CreatePhenotypicFeatureTest(APITestCase):

	def setUp(self):
		valid_payload = valid_phenotypic_feature()
		removed_pftype = valid_payload.pop('pftype', None)
		valid_payload['type'] = {
					"id": "HP:0000520",
					"label": "Proptosis"
				}
		self.valid_phenotypic_feature = valid_payload
		invalid_payload = invalid_phenotypic_feature()
		invalid_payload['type'] = {
					"id": "HP:0000520",
					"label": "Proptosis"
				}
		self.invalid_phenotypic_feature = invalid_payload
		

	def test_create_phenotypic_feature(self):
		""" POST a new phenotypic feature. """

		response = self.client.post(
			reverse('phenotypicfeature-list'),
			data=json.dumps(self.valid_phenotypic_feature),
			content_type='application/json'
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(PhenotypicFeature.objects.count(), 1)

	def test_modifier(self):
		serializer = PhenotypicFeatureSerializer(data=self.invalid_phenotypic_feature)
		self.assertEqual(serializer.is_valid(), False)


class CreateProcedureTest(APITestCase):

	def setUp(self):
		self.valid_procedure = VALID_PROCEDURE_1
		self.duplicate_procedure = VALID_PROCEDURE_1
		self.valid_procedure_duplicate_code = VALID_PROCEDURE_2

	def test_procedure(self):
		response = self.client.post(
			reverse('procedure-list'),
			data=json.dumps(self.valid_procedure),
			content_type='application/json'
		)
		response_duplicate = self.client.post(
			reverse('procedure-list'),
			data=json.dumps(self.duplicate_procedure),
			content_type='application/json'
		)
		response_duplicate_code = self.client.post(
			reverse('procedure-list'),
			data=json.dumps(self.valid_procedure_duplicate_code),
			content_type='application/json'
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response_duplicate.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(Procedure.objects.count(), 2)


class CreateHtsFileTest(APITestCase):

	def setUp(self):
		self.hts_file = VALID_HTS_FILE

	def test_hts_file(self):
		response = self.client.post(
			reverse('htsfile-list'),
			data=json.dumps(self.hts_file),
			content_type='application/json'
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(HtsFile.objects.count(), 1)


class CreateGeneTest(APITestCase):

	def setUp(self):
		self.gene = VALID_GENE_1
		self.duplicate_gene = DUPLICATE_GENE_2
		self.invalid_gene = INVALID_GENE_2

	def test_gene(self):
		response = self.client.post(
			reverse('gene-list'),
			data=json.dumps(self.gene),
			content_type='application/json'
		)
		response_duplicate = self.client.post(
			reverse('gene-list'),
			data=json.dumps(self.duplicate_gene),
			content_type='application/json'
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response_duplicate.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(Gene.objects.count(), 1)

	def test_alternate_ids(self):
		serializer = GeneSerializer(data=self.invalid_gene)
		self.assertEqual(serializer.is_valid(), False)


class CreateVariantTest(APITestCase):

	def setUp(self):
		self.variant = VALID_VARIANT_1

	def test_variant(self):
		response = self.client.post(
			reverse('variant-list'),
			data=json.dumps(self.variant),
			content_type='application/json'
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Variant.objects.count(), 1)

	# TODO test to_representation and to_internal_value
