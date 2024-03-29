from rest_framework import status
from rest_framework.test import APITestCase

from chord_metadata_service.patients.models import Individual
from chord_metadata_service.patients.tests.constants import VALID_INDIVIDUAL, VALID_INDIVIDUAL_2
from chord_metadata_service.phenopackets.models import (
    MetaData,
    Biosample,
    Phenopacket,
    PhenotypicFeature,
)
from chord_metadata_service.phenopackets.tests.constants import (
    VALID_INDIVIDUAL_1,
    VALID_META_DATA_2,
    VALID_PROCEDURE_1,
    VALID_DISEASE_1,
    valid_biosample_1,
    valid_biosample_2,
    valid_phenotypic_feature,
)
from chord_metadata_service.restapi.tests.utils import get_post_response


# Tests for FHIR conversion functions


class FHIRPhenopacketTest(APITestCase):

    def setUp(self):
        self.subject = Individual.objects.create(**VALID_INDIVIDUAL_1)
        self.metadata = MetaData.objects.create(**VALID_META_DATA_2)
        self.biosample_1 = Biosample.objects.create(**valid_biosample_1(self.subject))
        self.biosample_2 = Biosample.objects.create(**valid_biosample_2(None, VALID_PROCEDURE_1))
        self.phenopacket = Phenopacket.objects.create(
            id="phenopacket_id:1",
            subject=self.subject,
            meta_data=self.metadata,
        )
        self.phenopacket.biosamples.set([self.biosample_1, self.biosample_2])

    def test_get_fhir(self):
        get_resp = self.client.get('/api/phenopackets?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertEqual(get_resp_obj['compositions'][0]['resourceType'], 'Composition')
        self.assertEqual(get_resp_obj['compositions'][0]['title'], 'Phenopacket')
        self.assertEqual(get_resp_obj['compositions'][0]['type']['coding'][0]['system'],
                         'http://ga4gh.org/fhir/phenopackets/CodeSystem/document-type')
        self.assertEqual(get_resp_obj['compositions'][0]['status'], 'preliminary')
        self.assertIsInstance(get_resp_obj['compositions'][0]['subject']['reference'], str)
        self.assertIsInstance(get_resp_obj['compositions'][0]['section'], list)
        self.assertIsInstance(get_resp_obj['compositions'][0]['section'][0]['code']['coding'], list)
        self.assertEqual(get_resp_obj['compositions'][0]['section'][0]['code']['coding'][0]['code'],
                         'biosamples')
        self.assertEqual(get_resp_obj['compositions'][0]['section'][0]['code']['coding'][0]['display'],
                         'Biosamples')
        self.assertEqual(get_resp_obj['compositions'][0]['section'][0]['code']['coding'][0]['system'],
                         'http://ga4gh.org/fhir/phenopackets/CodeSystem/section-type')
        self.assertEqual(get_resp_obj['compositions'][0]['section'][0]['code']['coding'][0]['version'],
                         '0.1.0')
        self.assertIsInstance(get_resp_obj['compositions'][0]['section'][0]['entry'], list)
        self.assertEqual(len(get_resp_obj['compositions'][0]['section'][0]['entry']), 2)


class FHIRIndividualTest(APITestCase):
    """ Test module for creating an Individual. """

    def setUp(self):
        self.individual = Individual.objects.create(**VALID_INDIVIDUAL)
        self.individual_second = Individual.objects.create(**VALID_INDIVIDUAL_2)

    def test_get_fhir(self):
        get_resp = self.client.get('/api/individuals?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertEqual(get_resp_obj['patients'][0]['resourceType'], 'Patient')
        self.assertIsInstance(get_resp_obj['patients'][0]['extension'], list)
        self.assertEqual(get_resp_obj['patients'][1]['extension'][0]['url'],
                         'http://ga4gh.org/fhir/phenopackets/StructureDefinition/individual-karyotypic-sex')
        self.assertEqual(get_resp_obj['patients'][1]['extension'][1]['url'],
                         'http://ga4gh.org/fhir/phenopackets/StructureDefinition/individual-taxonomy')
        self.assertEqual(get_resp_obj['patients'][1]['extension'][2]['url'],
                         'http://ga4gh.org/fhir/phenopackets/StructureDefinition/individual-birthdate')
        self.assertIsInstance(get_resp_obj['patients'][1]['extension'][2]['valueDate'], str)


class FHIRPhenotypicFeatureTest(APITestCase):

    def setUp(self):
        self.individual_1 = Individual.objects.create(**VALID_INDIVIDUAL_1)
        self.individual_2 = Individual.objects.create(**VALID_INDIVIDUAL_2)
        self.biosample_1 = Biosample.objects.create(**valid_biosample_1(self.individual_1))
        self.biosample_2 = Biosample.objects.create(**valid_biosample_2(
            self.individual_2, VALID_PROCEDURE_1))
        self.phenotypic_feature_1 = PhenotypicFeature.objects.create(
            **valid_phenotypic_feature(biosample=self.biosample_1))
        self.phenotypic_feature_2 = PhenotypicFeature.objects.create(
            **valid_phenotypic_feature(biosample=self.biosample_2))

    def test_get_fhir(self):
        get_resp = self.client.get('/api/phenotypicfeatures?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        severity = {
            'url': 'http://ga4gh.org/fhir/phenopackets/StructureDefinition/phenotypic-feature-severity',
            'valueCodeableConcept': {
                'coding': [
                    {
                        'code': 'HP: 0012825',
                        'display': 'Mild'
                    }
                ]
            }
        }
        self.assertEqual(get_resp_obj['observations'][0]['resourceType'], 'Observation')
        self.assertIsInstance(get_resp_obj['observations'][0]['extension'], list)
        self.assertIn(severity, get_resp_obj['observations'][0]['extension'])
        self.assertEqual(get_resp_obj['observations'][0]['status'], 'unknown')
        self.assertEqual(get_resp_obj['observations'][0]['code']['coding'][0]['display'], 'Proptosis')
        self.assertEqual(get_resp_obj['observations'][0]['interpretation']['coding'][0]['code'], 'POS')
        self.assertEqual(get_resp_obj['observations'][0]['extension'][3]['url'],
                         'http://ga4gh.org/fhir/phenopackets/StructureDefinition/evidence')
        self.assertEqual(get_resp_obj['observations'][0]['extension'][3]['extension'][1]['extension'][1]['url'],
                         'description')
        self.assertIsNotNone(get_resp_obj['observations'][0]['specimen'])
        self.assertIsInstance(get_resp_obj['observations'][0]['specimen'], dict)
        self.assertEqual(get_resp_obj['observations'][0]['specimen']['reference'], 'katsu.biosample_id:1')


class FHIRBiosampleTest(APITestCase):
    """ Test module for creating an Biosample. """

    def setUp(self):
        self.individual = Individual.objects.create(**VALID_INDIVIDUAL_1)
        self.procedure = VALID_PROCEDURE_1
        self.valid_payload = valid_biosample_1(self.individual.id, self.procedure)

    def test_get_fhir(self):
        """ POST a new biosample. """

        get_post_response('biosamples-list', self.valid_payload)
        get_resp = self.client.get('/api/biosamples?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertEqual(get_resp_obj['specimens'][0]['resourceType'], 'Specimen')
        self.assertIsNotNone(get_resp_obj['specimens'][0]['type']['coding'][0])
        self.assertIsNotNone(get_resp_obj['specimens'][0]['collection'])
        self.assertIsInstance(get_resp_obj['specimens'][0]['extension'][0]['valueAge'], dict)
        self.assertEqual(get_resp_obj['specimens'][0]['extension'][4]['url'],
                         'http://ga4gh.org/fhir/phenopackets/StructureDefinition/biosample-diagnostic-markers')
        self.assertIsInstance(get_resp_obj['specimens'][0]['extension'][4]['valueCodeableConcept']['coding'],
                              list)


class FHIRDiseaseTest(APITestCase):

    def setUp(self):
        self.disease = VALID_DISEASE_1

    def test_get_fhir(self):
        get_post_response('diseases-list', self.disease)
        get_resp = self.client.get('/api/diseases?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertEqual(get_resp_obj['conditions'][0]['resourceType'], 'Condition')
        self.assertIsNotNone(get_resp_obj['conditions'][0]['code']['coding'][0])
        self.assertIsInstance(get_resp_obj['conditions'][0]['extension'], list)
        self.assertEqual(get_resp_obj['conditions'][0]['extension'][0]['url'],
                         'http://ga4gh.org/fhir/phenopackets/StructureDefinition/disease-tumor-stage')
        self.assertEqual(get_resp_obj['conditions'][0]['subject']['reference'], 'unknown')
