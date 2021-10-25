from rest_framework import status
from rest_framework.test import APITestCase
from . import constants as c
from .. import models as m, serializers as s
from chord_metadata_service.restapi.tests.utils import get_response
from django.urls import reverse


class BiosapleSampledTissueAutocompleteTest(APITestCase):
    """ Test module for creating an Biosample. """

    def setUp(self):
        self.individual = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.procedure = m.Procedure.objects.create(**c.VALID_PROCEDURE_1)
        self.biosample_1 = m.Biosample.objects.create(**c.valid_biosample_1(self.individual, self.procedure))
        self.biosample_2 = m.Biosample.objects.create(**c.valid_biosample_2(self.individual, self.procedure))

    def test_autocomplete_response(self):
        response = self.client.get('/api/biosample_sampled_tissue_autocomplete', {'q': 'bladder'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 2)

    def test_autocomplete_response_2(self):
        response = self.client.get('/api/biosample_sampled_tissue_autocomplete', {'q': 'wall'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 1)
