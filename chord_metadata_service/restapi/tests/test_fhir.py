from rest_framework.test import APITestCase
from chord_metadata_service.phenopackets.tests.constants import *
from chord_metadata_service.patients.tests.constants import *
from chord_metadata_service.phenopackets.tests.test_api import get_response
from chord_metadata_service.phenopackets.serializers import *
from rest_framework import status


class FHIRPhenopacketTest(APITestCase):

    def setUp(self):
        individual = Individual.objects.create(**VALID_INDIVIDUAL_1)
        self.subject = individual.id
        meta = MetaData.objects.create(**VALID_META_DATA_2)
        self.metadata = meta.id
        self.phenopacket = valid_phenopacket(
            subject=self.subject,
            meta_data=self.metadata)


    def test_get_fhir(self):
        response = get_response('phenopacket-list', self.phenopacket)
        get_resp = self.client.get('/api/phenopackets?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertEqual(get_resp_obj['compositions'][0]['resourceType'], 'Composition')
        self.assertEqual(get_resp_obj['compositions'][0]['title'], 'Phenopacket')
        self.assertEqual(get_resp_obj['compositions'][0]['type']['coding'][0]['system'],
                         'http://ga4gh.org/fhir/phenopackets/CodeSystem/document-type')
        self.assertEqual(get_resp_obj['compositions'][0]['status'], 'preliminary')
        self.assertIsInstance(get_resp_obj['compositions'][0]['subject']['reference'], str)


class FHIRIndividualTest(APITestCase):
    """ Test module for creating an Individual. """

    def setUp(self):
        self.individual = VALID_INDIVIDUAL

    def test_create_individual(self):
        response = get_response('individual-list', self.individual)
        get_resp = self.client.get('/api/individuals?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertEqual(get_resp_obj['patients'][0]['resourceType'], 'Patient')
        self.assertIsInstance(get_resp_obj['patients'][0]['extension'], list)
