from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from chord_metadata_service.metadata.service_info import SERVICE_INFO
from chord_metadata_service.phenopackets import models as ph_m
from chord_metadata_service.phenopackets.tests import constants as ph_c


class ServiceInfoTest(APITestCase):
    def test_service_info(self):
        r = self.client.get(reverse("service-info"), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertDictEqual(r.json(), SERVICE_INFO)

        # TODO: Test compliance with spec


class OverviewTest(APITestCase):

    def setUp(self) -> None:
        # create 2 phenopackets for 2 individuals; each individual has 1 biosample;
        # one of phenopackets has 1 phenotypic feature and 1 disease
        self.individual_1 = ph_m.Individual.objects.create(**ph_c.VALID_INDIVIDUAL_1)
        self.individual_2 = ph_m.Individual.objects.create(**ph_c.VALID_INDIVIDUAL_2)
        self.metadata_1 = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_1)
        self.metadata_2 = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_2)
        self.phenopacket_1 = ph_m.Phenopacket.objects.create(
            **ph_c.valid_phenopacket(subject=self.individual_1, meta_data=self.metadata_1)
        )
        self.phenopacket_2 = ph_m.Phenopacket.objects.create(
            id='phenopacket:2', subject=self.individual_2, meta_data=self.metadata_2
        )
        self.disease = ph_m.Disease.objects.create(**ph_c.VALID_DISEASE_1)
        self.procedure = ph_m.Procedure.objects.create(**ph_c.VALID_PROCEDURE_1)
        self.biosample_1 = ph_m.Biosample.objects.create(**ph_c.valid_biosample_1(self.individual_1, self.procedure))
        self.biosample_2 = ph_m.Biosample.objects.create(**ph_c.valid_biosample_2(self.individual_2, self.procedure))
        self.phenotypic_feature = ph_m.PhenotypicFeature.objects.create(
            **ph_c.valid_phenotypic_feature(self.biosample_1, self.phenopacket_1)
        )
        self.phenopacket_1.biosamples.set([self.biosample_1])
        self.phenopacket_2.biosamples.set([self.biosample_2])
        self.phenopacket_1.diseases.set([self.disease])

    def test_overview(self):
        response = self.client.get('/api/overview')
        response_obj = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj['phenopackets'], 2)
        self.assertEqual(response_obj['data_type_specific']['individuals']['count'], 2)
        self.assertEqual(response_obj['data_type_specific']['biosamples']['count'], 2)
        self.assertEqual(response_obj['data_type_specific']['phenotypic_features']['count'], 1)
        self.assertEqual(response_obj['data_type_specific']['diseases']['count'], 1)
