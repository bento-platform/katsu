from rest_framework.test import APITestCase
from chord_metadata_service.phenopackets.tests.constants import *
from chord_metadata_service.patients.tests.constants import *
from chord_metadata_service.phenopackets.tests.test_api import get_response
from chord_metadata_service.phenopackets.serializers import *
from rest_framework import status

# Tests for FHIR conversion functions

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
        self.individual_second = VALID_INDIVIDUAL_2

    def test_get_fhir(self):
        response_1 = get_response('individual-list', self.individual)
        response_2 = get_response('individual-list', self.individual_second)
        get_resp = self.client.get('/api/individuals?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertEqual(get_resp_obj['patients'][0]['resourceType'], 'Patient')
        self.assertIsInstance(get_resp_obj['patients'][0]['extension'], list)
        self.assertEqual(get_resp_obj['patients'][1]['extension'][0]['url'],
                         'http://ga4gh.org/fhir/phenopackets/StructureDefinition/individual-age')
        self.assertIsInstance(get_resp_obj['patients'][1]['extension'][0]['valueAge'], dict)


class FHIRPhenotypicFeatureTest(APITestCase):

    def setUp(self):
        valid_payload = valid_phenotypic_feature()
        removed_pftype = valid_payload.pop('pftype', None)
        valid_payload['type'] = {
            "id": "HP:0000520",
            "label": "Proptosis"
        }
        self.valid_phenotypic_feature = valid_payload


    def test_get_fhir(self):
        response = get_response('phenotypicfeature-list', self.valid_phenotypic_feature)
        get_resp = self.client.get('/api/phenotypicfeatures?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        severity = {
            'url':'http://ga4gh.org/fhir/phenopackets/StructureDefinition/phenotypic-feature-severity',
            'valueCodeableConcept':{
                'coding':[
                    {
                    'code':'HP: 0012825',
                    'display':'Mild'
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


class FHIRBiosampleTest(APITestCase):
    """ Test module for creating an Biosample. """

    def setUp(self):
        self.individual = Individual.objects.create(**VALID_INDIVIDUAL_1)
        self.procedure = VALID_PROCEDURE_1
        self.valid_payload = valid_biosample_1(self.individual.id, self.procedure)

    def test_create_biosample(self):
        """ POST a new biosample. """

        response = get_response('biosample-list', self.valid_payload)
        get_resp = self.client.get('/api/biosamples?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertEqual(get_resp_obj['specimens'][0]['resourceType'], 'Specimen')
        self.assertIsNotNone(get_resp_obj['specimens'][0]['type']['coding'][0])
        self.assertIsNotNone(get_resp_obj['specimens'][0]['collection'])
        self.assertIsInstance(get_resp_obj['specimens'][0]['extension'][0]['valueRange'], dict)
        self.assertEqual(get_resp_obj['specimens'][0]['extension'][4]['url'],
                         'http://ga4gh.org/fhir/phenopackets/StructureDefinition/biosample-diagnostic-markers')
        self.assertIsInstance(get_resp_obj['specimens'][0]['extension'][4]['valueCodeableConcept']['coding'],
                         list)
        self.assertTrue(get_resp_obj['specimens'][0]['extension'][5]['valueBoolean'])


class FHIRHtsFileTest(APITestCase):

    def setUp(self):
        self.hts_file = VALID_HTS_FILE

    def test_hts_file(self):
        response = get_response('htsfile-list', self.hts_file)
        get_resp = self.client.get('/api/htsfiles?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertEqual(get_resp_obj['document_references'][0]['resourceType'], 'DocumentReference')
        self.assertIsInstance(get_resp_obj['document_references'][0]['content'], list)
        self.assertIsNotNone(get_resp_obj['document_references'][0]['content'][0]['attachment']['url'])
        self.assertEqual(get_resp_obj['document_references'][0]['status'], 'current')
        self.assertEqual(get_resp_obj['document_references'][0]['type']['coding'][0]['code'],
                         get_resp_obj['document_references'][0]['type']['coding'][0]['display'])
        self.assertEqual(get_resp_obj['document_references'][0]['extension'][0]['url'],
                         'http://ga4gh.org/fhir/phenopackets/StructureDefinition/htsfile-genome-assembly')


class FHIRGeneTest(APITestCase):

    def setUp(self):
        self.gene = VALID_GENE_1

    def test_gene(self):
        response = get_response('gene-list', self.gene)
        get_resp = self.client.get('/api/genes?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertIsInstance(get_resp_obj['observations'], list)
        self.assertIsInstance(get_resp_obj['observations'][0]['code']['coding'], list)
        self.assertEqual(get_resp_obj['observations'][0]['code']['coding'][0]['code'], '48018-6')
        self.assertEqual(get_resp_obj['observations'][0]['code']['coding'][0]['display'], 'Gene studied [ID]')
        self.assertEqual(get_resp_obj['observations'][0]['code']['coding'][0]['system'], 'https://loinc.org')
        self.assertIsInstance(get_resp_obj['observations'][0]['valueCodeableConcept']['coding'], list)
        self.assertEqual(get_resp_obj['observations'][0]['valueCodeableConcept']['coding'][0]['system'],
                         'https://www.genenames.org/')


class FHIRVariantTest(APITestCase):

    def setUp(self):
        self.variant = VALID_VARIANT_1

    def test_variant(self):
        response = get_response('variant-list', self.variant)
        get_resp = self.client.get('/api/variants?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertIsInstance(get_resp_obj['observations'], list)
        self.assertIsInstance(get_resp_obj['observations'][0]['code']['coding'], list)
        self.assertEqual(get_resp_obj['observations'][0]['code']['coding'][0]['code'], '81300-6')
        self.assertEqual(get_resp_obj['observations'][0]['code']['coding'][0]['display'], 'Structural variant [Length]')
        self.assertEqual(get_resp_obj['observations'][0]['code']['coding'][0]['system'], 'https://loinc.org')
        self.assertEqual(get_resp_obj['observations'][0]['valueCodeableConcept']['coding'][0]['code'],
                         get_resp_obj['observations'][0]['valueCodeableConcept']['coding'][0]['display'])


class FHIRDiseaseTest(APITestCase):

    def setUp(self):
        self.disease = VALID_DISEASE_1

    def test_disease(self):
        response = get_response('disease-list', self.disease)
        get_resp = self.client.get('/api/diseases?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertEqual(get_resp_obj['conditions'][0]['resourceType'], 'Condition')
        self.assertIsNotNone(get_resp_obj['conditions'][0]['code']['coding'][0])
        self.assertIsInstance(get_resp_obj['conditions'][0]['extension'], list)
        self.assertEqual(get_resp_obj['conditions'][0]['extension'][0]['url'],
                              'http://ga4gh.org/fhir/phenopackets/StructureDefinition/disease-tumor-stage')
        self.assertEqual(get_resp_obj['conditions'][0]['subject']['reference'], 'unknown')
        