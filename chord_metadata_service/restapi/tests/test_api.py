import json
import os
from copy import deepcopy

from django.conf import settings
from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from chord_metadata_service.metadata.service_info import SERVICE_INFO
from chord_metadata_service.chord import models as ch_m
from chord_metadata_service.chord.tests import constants as ch_c
from chord_metadata_service.phenopackets import models as ph_m
from chord_metadata_service.phenopackets.tests import constants as ph_c
from chord_metadata_service.experiments import models as exp_m
from chord_metadata_service.experiments.tests import constants as exp_c
from chord_metadata_service.mcode import models as mcode_m
from chord_metadata_service.mcode.tests import constants as mcode_c

from .constants import (
    CONFIG_PUBLIC_TEST,
    CONFIG_PUBLIC_TEST_SEARCH_UNSET_FIELDS,
    VALID_INDIVIDUALS,
    INDIVIDUALS_NOT_ACCEPTED_DATA_TYPES_LIST,
    INDIVIDUALS_NOT_ACCEPTED_DATA_TYPES_DICT
)


class ServiceInfoTest(APITestCase):
    def test_service_info(self):
        r = self.client.get(reverse("service-info"), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertDictEqual(r.json(), SERVICE_INFO)

        # TODO: Test compliance with spec


class ExtraPropertiesSchemaTypesTest(APITestCase):
    def test_extra_properties_schema_types(self):
        response = self.client.get('/api/extra_properties_schema_types')
        response_obj = response.json()
        expected_response = {
            "PHENOPACKET": "Phenopacket",
            "BIOSAMPLE": "Biosample",
            "INDIVIDUAL": "Individual"
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_obj, expected_response)


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
        exp_m.Experiment.objects.create(**exp_c.valid_experiment(self.biosample_2, self.instrument, num_experiment=2))
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
        self.assertEqual(
            response_obj['data_type_specific']['individuals']['age'],
            {**{'40': 1, '30': 1}, **response_obj['data_type_specific']['individuals']['age']})
        self.assertEqual(response_obj['data_type_specific']['biosamples']['count'], 2)
        self.assertEqual(response_obj['data_type_specific']['phenotypic_features']['count'], 1)
        self.assertEqual(response_obj['data_type_specific']['diseases']['count'], 1)
        # experiments
        self.assertEqual(response_obj['data_type_specific']['experiments']['count'], 2)
        self.assertEqual(response_obj['data_type_specific']['experiments']['study_type']['Whole genome Sequencing'], 2)
        self.assertEqual(
            response_obj['data_type_specific']['experiments']['experiment_type']['DNA Methylation'], 2
        )
        self.assertEqual(response_obj['data_type_specific']['experiments']['molecule']['total RNA'], 2)
        self.assertEqual(response_obj['data_type_specific']['experiments']['library_strategy']['Bisulfite-Seq'], 2)
        self.assertEqual(response_obj['data_type_specific']['experiments']['library_source']['Genomic'], 2)
        self.assertEqual(response_obj['data_type_specific']['experiments']['library_selection']['PCR'], 2)
        self.assertEqual(response_obj['data_type_specific']['experiments']['library_layout']['Single'], 2)
        self.assertEqual(response_obj['data_type_specific']['experiments']['extraction_protocol']['NGS'], 2)
        self.assertEqual(response_obj['data_type_specific']['experiment_results']['count'], 1)
        self.assertEqual(response_obj['data_type_specific']['experiment_results']['file_format']['VCF'], 1)
        self.assertEqual(
            response_obj['data_type_specific']['experiment_results']['data_output_type']['Derived data'], 1
        )
        self.assertEqual(response_obj['data_type_specific']['experiment_results']['usage']['download'], 1)
        self.assertEqual(response_obj['data_type_specific']['instruments']['count'], 1)
        self.assertEqual(response_obj['data_type_specific']['instruments']['platform']['Illumina'], 2)
        self.assertEqual(response_obj['data_type_specific']['instruments']['model']['Illumina HiSeq 4000'], 2)

    def test_search_overview(self):
        payload = json.dumps({'id': [ph_c.VALID_INDIVIDUAL_1['id']]})
        response = self.client.post(reverse('search-overview'), payload, content_type='application/json')
        response_obj = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj['biosamples']['count'], 1)
        self.assertIn('wall of urinary bladder', response_obj['biosamples']['sampled_tissue'])
        self.assertIn('Proptosis', response_obj['phenotypic_features']['type'])
        self.assertIn(ph_c.VALID_DISEASE_1['term']['label'], response_obj['diseases']['term'])


class McodeOverviewTest(APITestCase):
    # create 2 mcodepackets for 2 individuals
    def setUp(self) -> None:
        self.individual = ph_m.Individual.objects.create(**mcode_c.VALID_INDIVIDUAL)
        self.individual_2 = ph_m.Individual.objects.create(**ph_c.VALID_INDIVIDUAL_2)
        self.labs_vital = mcode_m.LabsVital.objects.create(**mcode_c.valid_labs_vital(self.individual))
        self.genomics_report = mcode_m.GenomicsReport.objects.create(**mcode_c.valid_genetic_report())
        self.cancer_condition = mcode_m.CancerCondition.objects.create(**mcode_c.valid_cancer_condition())
        self.cancer_condition_2 = mcode_m.CancerCondition.objects.create(**mcode_c.VALID_CANCER_CONDITION)
        self.tnm_staging = mcode_m.TNMStaging.objects.create(**mcode_c.invalid_tnm_staging(self.cancer_condition))
        self.cancer_related_procedure = mcode_m.CancerRelatedProcedure.objects.create(
            **mcode_c.valid_cancer_related_procedure()
        )
        self.medication_statement = mcode_m.MedicationStatement.objects.create(**mcode_c.valid_medication_statement())
        self.mcodepacket_1 = mcode_m.MCodePacket.objects.create(
            id="mcodepacket:01",
            subject=self.individual,
            genomics_report=self.genomics_report,
            cancer_disease_status={
                "id": "SNOMED:268910001",
                "label": "Patient's condition improved"
            },
            cancer_condition=self.cancer_condition
        )
        self.mcodepacket_1.cancer_related_procedures.set([self.cancer_related_procedure])
        self.mcodepacket_1.medication_statement.set([self.medication_statement])
        self.mcodepacket_2 = mcode_m.MCodePacket.objects.create(
            id="mcodepacket:02",
            subject=self.individual_2,
            cancer_disease_status={
                "id": "SNOMED:359746009",
                "label": "Patient's condition stable"
            },
            cancer_condition=self.cancer_condition_2
        )

    def test_mcode_overview(self):
        response = self.client.get("/api/mcode_overview")
        response_obj = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_obj, dict)
        # mcodepackets
        self.assertEqual(response_obj["mcodepackets"], 2)
        self.assertEqual(response_obj["data_type_specific"]["cancer_conditions"]["count"], 2)
        self.assertEqual(response_obj["data_type_specific"]["cancer_related_procedure_types"]["count"], 1)
        self.assertEqual(response_obj["data_type_specific"]["cancer_related_procedures"]["count"], 1)
        self.assertEqual(response_obj["data_type_specific"]["cancer_disease_status"]["count"], 2)
        self.assertEqual(response_obj["data_type_specific"]["individuals"]["count"], 2)


class PublicSearchFieldsTest(APITestCase):

    def setUp(self) -> None:
        # create 2 phenopackets for 2 individuals; each individual has 1 biosample;
        # one of phenopackets has 1 phenotypic feature and 1 disease
        self.individual_1 = ph_m.Individual.objects.create(**ph_c.VALID_INDIVIDUAL_1)
        self.metadata_1 = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_1)
        self.phenopacket_1 = ph_m.Phenopacket.objects.create(
            **ph_c.valid_phenopacket(subject=self.individual_1, meta_data=self.metadata_1)
        )
        self.disease = ph_m.Disease.objects.create(**ph_c.VALID_DISEASE_1)
        self.procedure = ph_m.Procedure.objects.create(**ph_c.VALID_PROCEDURE_1)
        self.biosample_1 = ph_m.Biosample.objects.create(**ph_c.valid_biosample_1(self.individual_1, self.procedure))
        self.phenotypic_feature = ph_m.PhenotypicFeature.objects.create(
            **ph_c.valid_phenotypic_feature(self.biosample_1, self.phenopacket_1)
        )
        self.phenopacket_1.biosamples.set([self.biosample_1])
        self.phenopacket_1.diseases.set([self.disease])

        # experiments
        self.instrument = exp_m.Instrument.objects.create(**exp_c.valid_instrument())
        self.experiment = exp_m.Experiment.objects.create(**exp_c.valid_experiment(self.biosample_1, self.instrument))
        self.experiment_result = exp_m.ExperimentResult.objects.create(**exp_c.valid_experiment_result())
        self.experiment.experiment_results.set([self.experiment_result])

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_public_search_fields_configured(self):
        response = self.client.get(reverse("public-search-fields"), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        self.assertSetEqual(
            set(field["id"] for section in response_obj["sections"] for field in section["fields"]),
            set(field for section in settings.CONFIG_PUBLIC["search"] for field in section["fields"])
        )

    @override_settings(CONFIG_PUBLIC={})
    def test_public_search_fields_not_configured(self):
        response = self.client.get(reverse("public-search-fields"), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj, settings.NO_PUBLIC_FIELDS_CONFIGURED)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST_SEARCH_UNSET_FIELDS)
    def test_public_search_fields_missing_extra_properties(self):
        response = self.client.get(reverse("public-search-fields"), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_obj = response.json()
        self.assertSetEqual(
            set(field["id"] for section in response_obj["sections"] for field in section["fields"]),
            set(field for section in settings.CONFIG_PUBLIC["search"] for field in section["fields"])
        )


class PublicOverviewTest(APITestCase):

    def setUp(self) -> None:
        # individuals (count 8)
        individuals = {
            f"individual_{i}": ph_m.Individual.objects.create(**ind) for i, ind in enumerate(VALID_INDIVIDUALS, start=1)
        }
        # biosamples
        self.procedure = ph_m.Procedure.objects.create(**ph_c.VALID_PROCEDURE_1)
        self.biosample_1 = ph_m.Biosample.objects.create(
            **ph_c.valid_biosample_1(individuals["individual_1"], self.procedure)
        )
        self.biosample_2 = ph_m.Biosample.objects.create(
            **ph_c.valid_biosample_2(individuals["individual_2"], self.procedure)
        )
        # experiments
        self.instrument = exp_m.Instrument.objects.create(**exp_c.valid_instrument())
        self.experiment = exp_m.Experiment.objects.create(**exp_c.valid_experiment(self.biosample_1, self.instrument))
        self.experiment_result = exp_m.ExperimentResult.objects.create(**exp_c.valid_experiment_result())
        self.experiment.experiment_results.set([self.experiment_result])
        # make a copy and create experiment 2
        experiment_2 = deepcopy(exp_c.valid_experiment(self.biosample_2, self.instrument))
        experiment_2["id"] = "experiment:2"
        self.experiment = exp_m.Experiment.objects.create(**experiment_2)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_overview(self):
        response = self.client.get('/api/public_overview')
        response_obj = response.json()
        db_count = ph_m.Individual.objects.all().count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj["counts"]["individuals"], db_count)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_overview_bins(self):
        # test that there is the correct number of data entries for number
        # histograms, vs. number of bins
        response = self.client.get('/api/public_overview')
        response_obj = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(
            # 1 more bin than intervals expected: e.g. for config.bins = [2, 3, 4],
            # we expect data entries for ≤2, [2 3), [3 4), ≥4
            len(response_obj["fields"]["lab_test_result_value"]["config"]["bins"]) + 1,
            len(response_obj["fields"]["lab_test_result_value"]["data"]),
        )

    @override_settings(CONFIG_PUBLIC={})
    def test_overview_no_config(self):
        response = self.client.get('/api/public_overview')
        response_obj = response.json()
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj, settings.NO_PUBLIC_DATA_AVAILABLE)


class PublicOverviewTest2(APITestCase):

    def setUp(self) -> None:
        # create only 2 individuals
        for ind in VALID_INDIVIDUALS[:2]:
            ph_m.Individual.objects.create(**ind)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_overview_response(self):
        # test overview response when individuals count < threshold
        response = self.client.get('/api/public_overview')
        response_obj = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_obj, dict)
        self.assertNotIn("counts", response_obj)
        self.assertEqual(response_obj, settings.INSUFFICIENT_DATA_AVAILABLE)

    @override_settings(CONFIG_PUBLIC={})
    def test_overview_response_no_config(self):
        # test overview response when individuals count < threshold
        response = self.client.get('/api/public_overview')
        response_obj = response.json()
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj, settings.NO_PUBLIC_DATA_AVAILABLE)


class PublicOverviewNotSupportedDataTypesListTest(APITestCase):
    # individuals (count 8)
    def setUp(self) -> None:
        # create individuals including those who have not accepted data types
        for ind in INDIVIDUALS_NOT_ACCEPTED_DATA_TYPES_LIST:
            ph_m.Individual.objects.create(**ind)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_overview_response(self):
        # test overview response with passing TypeError exception
        response = self.client.get('/api/public_overview')
        response_obj = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_obj, dict)
        # the field name is present, but the keys are not (except 'missing')
        self.assertIn("baseline_creatinine", response_obj["fields"])
        self.assertIn("missing", response_obj["fields"]["baseline_creatinine"]["data"][-1]["label"])
        self.assertEqual(8, response_obj["fields"]["baseline_creatinine"]["data"][-1]["value"])
        # if we add support for an array values for the public_overview
        # then this assertion will fail, so far there is no support for it
        self.assertNotIn(
            100,
            [data["value"] for data in response_obj["fields"]["baseline_creatinine"]["data"]])


class PublicOverviewNotSupportedDataTypesDictTest(APITestCase):
    # individuals (count 8)
    def setUp(self) -> None:
        # create individuals including those who have not accepted data types
        for ind in INDIVIDUALS_NOT_ACCEPTED_DATA_TYPES_DICT:
            ph_m.Individual.objects.create(**ind)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_overview_response(self):
        # test overview response with passing TypeError exception
        response = self.client.get('/api/public_overview')
        response_obj = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_obj, dict)
        # the field name is present, but the keys are not (except 'missing')
        self.assertIn("baseline_creatinine", response_obj["fields"])
        self.assertIn("missing", response_obj["fields"]["baseline_creatinine"]["data"][-1]["label"])
        self.assertEqual(8, response_obj["fields"]["baseline_creatinine"]["data"][-1]["value"])


class PublicDatasetsMetadataTest(APITestCase):

    def setUp(self) -> None:
        project = ch_m.Project.objects.create(title="Test project", description="test description")
        dats_path = os.path.join(os.path.dirname(__file__), "example_dats_provenance.json")
        with open(dats_path) as f:
            dats_content = f.read()

        ch_m.Dataset.objects.create(
            title="Dataset 1",
            description="Test dataset",
            contact_info="Test contact info",
            types=["test type 1", "test type 2"],
            privacy="Open",
            keywords=["test keyword 1", "test keyword 2"],
            data_use=ch_c.VALID_DATA_USE_1,
            project=project,
            dats_file=dats_content
        )

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_public_dataset(self):
        response = self.client.get(reverse("public-dataset"))
        response_obj = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_obj, dict)

        # datasets
        self.assertIsInstance(response_obj["datasets"], list)
        for i, dataset in enumerate(response_obj["datasets"]):
            self.assertIn("title", dataset.keys())
            self.assertIsNotNone(dataset["title"])
            if i == 0:
                self.assertTrue("keywords" in dataset["dats_file"])

    @override_settings(CONFIG_PUBLIC={})
    def test_public_dataset_response_no_config(self):
        response = self.client.get(reverse("public-dataset"))
        response_obj = response.json()
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj, settings.NO_PUBLIC_DATA_AVAILABLE)
