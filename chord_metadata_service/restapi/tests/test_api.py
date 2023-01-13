from copy import deepcopy
from uuid import uuid4

from django.conf import settings
from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from chord_metadata_service.metadata.service_info import SERVICE_INFO
from chord_metadata_service.chord import models as ch_m
from chord_metadata_service.chord.tests import constants as ch_c
from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET
from chord_metadata_service.phenopackets import models as ph_m
from chord_metadata_service.phenopackets.tests import constants as ph_c
from chord_metadata_service.experiments import models as exp_m
from chord_metadata_service.experiments.tests import constants as exp_c

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
            response_obj['data_type_specific']['experiments']['experiment_type']['Chromatin Accessibility'], 2
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


class PublicOverviewDatasetsMetadataTest(APITestCase):

    def setUp(self) -> None:
        project = ch_m.Project.objects.create(title="Test project", description="test description")
        dataset = ch_m.Dataset.objects.create(
            title="Dataset 1",
            description="Test dataset",
            contact_info="Test contact info",
            types=["test type 1", "test type 2"],
            privacy="Open",
            keywords=["test keyword 1", "test keyword 2"],
            data_use=ch_c.VALID_DATA_USE_1,
            project=project
        )
        table_ownership = ch_m.TableOwnership.objects.create(
            table_id=str(uuid4()),
            service_id=str(uuid4()),
            service_artifact="phenopacket",
            dataset=dataset
        )
        table = ch_m.Table.objects.create(
            ownership_record=table_ownership, name="Test table 1", data_type=DATA_TYPE_PHENOPACKET
        )
        metadata = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_1)
        for i, ind in enumerate(VALID_INDIVIDUALS, start=1):
            new_individual = ph_m.Individual.objects.create(**ind)
            ph_m.Phenopacket.objects.create(
                id=f"phenopacket:{i}",
                subject=new_individual,
                meta_data=metadata,
                table=table
            )

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST)
    def test_overview(self):
        response = self.client.get('/api/public_overview')
        response_obj = response.json()
        db_count = ph_m.Individual.objects.all().count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_obj, dict)
        # counts
        self.assertEqual(response_obj["counts"]["individuals"], db_count)

        # datasets
        self.assertIsInstance(response_obj["datasets"], list)
        for dataset in response_obj["datasets"]:
            self.assertIn("title", dataset.keys())
            self.assertIsNotNone(dataset["title"])

        # layout
        self.assertIn("layout", response_obj)
        self.assertEqual(response_obj["layout"], settings.CONFIG_PUBLIC["overview"])

        # fields
        self.assertIn("fields", response_obj)
        self.assertSetEqual(
            set(response_obj["fields"].keys()),
            set(chart["field"] for section in settings.CONFIG_PUBLIC["overview"] for chart in section["charts"])
        )
