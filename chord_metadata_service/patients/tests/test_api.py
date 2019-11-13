import json
from django.urls import include, path, reverse
from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase
from ..models import Individual


class CreateIndividualTest(APITestCase):
	""" Test module for creating an Individual. """

	def setUp(self):

		self.valid_payload = {
			"individual_id": "patient:1",
			"taxonomy": {
				"id": "NCBITaxon:9606",
				"label": "human"
			},
			"date_of_birth": "2001-01-01",
			"age": "P25Y3M2D",
			"sex": "FEMALE",
			"active": True
		}

		self.invalid_payload = {
			"individual_id": "patient:1",
			"taxonomy": {
				"id": "NCBITaxon:9606"
			},
			"date_of_birth": "2001-01-01",
			"age": "P25Y3M2D",
			"sex": "FEM",
			"active": True
		}

	def test_create_individual(self):
		""" POST a new individual. """

		response = self.client.post(
			reverse('individual-list'),
			data=json.dumps(self.valid_payload),
			content_type='application/json'
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Individual.objects.count(), 1)
		self.assertEqual(Individual.objects.get().individual_id, 'patient:1')

	def test_create_invalid_individual(self):
		""" Try to POST a new individual with wrong params. """

		invalid_response = self.client.post(
			reverse('individual-list'),
			data=json.dumps(self.invalid_payload),
			content_type='application/json'
		)
		self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(Individual.objects.count(), 0)



