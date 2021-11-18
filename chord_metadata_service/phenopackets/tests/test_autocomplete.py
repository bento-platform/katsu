from rest_framework import status
from rest_framework.test import APITestCase
from . import constants as c
from .. import models as m


class DiseaseTermAutocompleteTest(APITestCase):
    """ Test module for disease terms autocomplete. """

    def setUp(self):
        self.disease_1 = m.Disease.objects.create(**c.VALID_DISEASE_1)

    def test_autocomplete_response(self):
        response = self.client.get('/api/disease_term_autocomplete', {'q': 'ataxia'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 1)


class PhenotypicFeatureTypemAutocompleteTest(APITestCase):
    """ Test module for phenotypic featute type autocomplete. """

    def setUp(self):
        self.individual_1 = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.individual_2 = m.Individual.objects.create(**c.VALID_INDIVIDUAL_2)
        self.procedure = m.Procedure.objects.create(**c.VALID_PROCEDURE_1)
        self.biosample_1 = m.Biosample.objects.create(**c.valid_biosample_1(
            self.individual_1, self.procedure)
                                                      )
        self.biosample_2 = m.Biosample.objects.create(**c.valid_biosample_2(
            self.individual_2, self.procedure)
                                                      )
        self.meta_data = m.MetaData.objects.create(**c.VALID_META_DATA_1)
        self.phenopacket = m.Phenopacket.objects.create(
            id='phenopacket_id:1',
            subject=self.individual_2,
            meta_data=self.meta_data,
        )
        self.phenotypic_feature_1 = m.PhenotypicFeature.objects.create(
            **c.valid_phenotypic_feature(biosample=self.biosample_1))
        self.phenotypic_feature_2 = m.PhenotypicFeature.objects.create(
            **c.valid_phenotypic_feature(biosample=self.biosample_2, phenopacket=self.phenopacket))

    def test_autocomplete_response(self):
        response = self.client.get('/api/phenotypic_feature_type_autocomplete', {'q': 'proptosis'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 1)


class BiosapleSampledTissueAutocompleteTest(APITestCase):
    """ Test module for sampled tissue label autocomplete. """

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
