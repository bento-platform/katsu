import json
from django.urls import include, path, reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import *
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS


class CreateBiosampleTest(APITestCase):
	""" Test module for creating an Biosample. """

	def setUp(self):
		self.individual = Individual.objects.create(
			individual_id='patient:1',
			sex='FEMALE',
			age='P67Y3M2D'
			)
		self.procedure = {
			"code": {
				"id": "NCIT:C28743",
				"label": "Punch Biopsy"
			},
			"body_site": {
				"id": "UBERON:0003403",
				"label": "skin of forearm"
			}
		}
		self.valid_payload = {
			"biosample_id": "biosample:1",
			"individual": self.individual.individual_id,
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
			"biosample_id": "biosample:1",
			"individual": self.individual.individual_id,
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

	def test_create_biosample(self):
		""" POST a new biosample. """

		response = self.client.post(
			reverse('biosample-list'),
			data=json.dumps(self.valid_payload),
			content_type='application/json'
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Biosample.objects.count(), 1)
		self.assertEqual(Biosample.objects.get().biosample_id, 'biosample:1')

	def test_create_invalid_biosample(self):
		""" POST a new biosample with invalid data. """

		invalid_response = self.client.post(
			reverse('biosample-list'),
			data=json.dumps(self.invalid_payload),
			content_type='application/json'
		)
		self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(Biosample.objects.count(), 0)
		