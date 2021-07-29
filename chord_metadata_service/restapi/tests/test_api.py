from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from chord_metadata_service.metadata.service_info import SERVICE_INFO
from chord_metadata_service.phenopackets import models as ph_m
from chord_metadata_service.phenopackets.tests import constants as ph_c
from chord_metadata_service.experiments import models as exp_m
from chord_metadata_service.experiments.tests import constants as exp_c


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

        # experiments
        self.instrument = exp_m.Instrument.objects.create(**exp_c.valid_instrument())
        self.experiment = exp_m.Experiment.objects.create(**exp_c.valid_experiment(self.biosample_1, self.instrument))
        self.experiment_result = exp_m.ExperimentResult.objects.create(**exp_c.valid_experiment_result())
        self.experiment.experiment_results.set([self.experiment_result])

    def test_overview(self):
        response = self.client.get('/api/overview')
        response_obj = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_obj, dict)
        # phenopackets
        self.assertEqual(response_obj['phenopackets'], 2)
        self.assertEqual(response_obj['data_type_specific']['individuals']['count'], 2)
        self.assertIsInstance(response_obj['data_type_specific']['individuals']['age'], dict)
        self.assertEqual(response_obj['data_type_specific']['biosamples']['count'], 2)
        self.assertEqual(response_obj['data_type_specific']['phenotypic_features']['count'], 1)
        self.assertEqual(response_obj['data_type_specific']['diseases']['count'], 1)
        # experiments
        self.assertEqual(response_obj['data_type_specific']['experiments']['count'], 1)
        self.assertEqual(response_obj['data_type_specific']['experiments']['study_type']['Whole genome Sequencing'], 1)
        self.assertEqual(
            response_obj['data_type_specific']['experiments']['experiment_type']['Chromatin Accessibility'], 1
        )
        self.assertEqual(response_obj['data_type_specific']['experiments']['molecule']['total RNA'], 1)
        self.assertEqual(response_obj['data_type_specific']['experiments']['library_strategy']['Bisulfite-Seq'], 1)
        self.assertEqual(response_obj['data_type_specific']['experiments']['library_source']['Genomic'], 1)
        self.assertEqual(response_obj['data_type_specific']['experiments']['library_selection']['PCR'], 1)
        self.assertEqual(response_obj['data_type_specific']['experiments']['library_layout']['Single'], 1)
        self.assertEqual(response_obj['data_type_specific']['experiments']['extraction_protocol']['NGS'], 1)
        self.assertEqual(response_obj['data_type_specific']['experiment_results']['count'], 1)
        self.assertEqual(response_obj['data_type_specific']['experiment_results']['file_format']['VCF'], 1)
        self.assertEqual(
            response_obj['data_type_specific']['experiment_results']['data_output_type']['Derived data'], 1
        )
        self.assertEqual(response_obj['data_type_specific']['experiment_results']['usage']['download'], 1)
        self.assertEqual(response_obj['data_type_specific']['instruments']['count'], 1)
        self.assertEqual(response_obj['data_type_specific']['instruments']['platform']['Illumina'], 1)
        self.assertEqual(response_obj['data_type_specific']['instruments']['model']['Illumina HiSeq 4000'], 1)
