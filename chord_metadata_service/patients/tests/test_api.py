import json
from django.urls import include, path, reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import Individual
from .assertions import assert_valid_schema
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS


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
		""" POST a new individual with invalid data. """

		if 'taxonomy' in self.invalid_payload:
			assert_valid_schema(self.invalid_payload.get('taxonomy'), ONTOLOGY_CLASS)
		invalid_response = self.client.post(
			reverse('individual-list'),
			data=json.dumps(self.invalid_payload),
			content_type='application/json'
		)
		self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(Individual.objects.count(), 0)


class UpdateIndividualTest(APITestCase):
	""" Test module for updating an existing Individual record. """

	def setUp(self):
		self.individual_one = Individual.objects.create(
			individual_id='patient:1',
			taxonomy={
				"id": "NCBITaxon:9606",
				"label": "human"
			},
			date_of_birth='2001-01-01',
			age='P25Y3M2D',
			sex='FEMALE',
			active=True
			)

		self.valid_payload = {
			"individual_id": "patient:1",
			"taxonomy": {
				"id": "NCBITaxon:9606",
				"label": "human"
			},
			"date_of_birth": "2001-01-01",
			"age": "P26Y3M2D",
			"sex": "FEMALE",
			"active": False
		}

		self.invalid_payload = {
			"individual_id": "patient:1",
			"taxonomy": {
				"id": "NCBITaxon:9606",
				"label": "human"
			},
			"date_of_birth": "2001-01-01",
			"age": "P26Y3M2D",
			"sex": "WOMEN",
			"active": False
		}

	def test_update_individual(self):
		""" PUT new data in an existing Individual record. """

		response = self.client.put(
			reverse(
				'individual-detail',
				kwargs={'pk': self.individual_one.individual_id}
				),
			data=json.dumps(self.valid_payload),
			content_type='application/json'
			)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_update_invalid_individual(self):
		""" PUT new invalid data in an existing Individual record. """

		response = self.client.put(
			reverse(
				'individual-detail',
				kwargs={'pk': self.individual_one.individual_id}
				),
			data=json.dumps(self.invalid_payload),
			content_type='application/json'
			)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeleteIndividualTest(APITestCase):
	""" Test module for deleting an existing Individual record. """

	def setUp(self):
		self.individual_one = Individual.objects.create(
			individual_id='patient:1',
			taxonomy={
				"id": "NCBITaxon:9606",
				"label": "human"
			},
			date_of_birth='2001-01-01',
			age='P25Y3M2D',
			sex='FEMALE',
			active=True
			)

	def test_delete_individual(self):
		""" DELETE an existing Individual record. """

		response = self.client.delete(
			reverse(
				'individual-detail',
				kwargs={'pk': self.individual_one.individual_id}
				)
			)
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

	def test_delete_non_existing_individual(self):
		""" DELETE a non-existing Individual record. """

		response = self.client.delete(
			reverse(
				'individual-detail',
				kwargs={'pk': 'patient:what'}
				)
			)
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
