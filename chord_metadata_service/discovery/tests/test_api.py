import json
import os
from copy import deepcopy
import uuid

from django.conf import settings
from django.urls import reverse
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from chord_metadata_service.chord import models as ch_m
from chord_metadata_service.chord.tests import constants as ch_c
from chord_metadata_service.discovery import responses as dres
from chord_metadata_service.discovery.schemas import DISCOVERY_SCHEMA
from chord_metadata_service.phenopackets import models as ph_m
from chord_metadata_service.phenopackets.tests import constants as ph_c
from chord_metadata_service.experiments import models as exp_m
from chord_metadata_service.experiments.tests import constants as exp_c

from chord_metadata_service.restapi.tests.constants import (
    VALID_INDIVIDUALS,
    INDIVIDUALS_NOT_ACCEPTED_DATA_TYPES_LIST,
    INDIVIDUALS_NOT_ACCEPTED_DATA_TYPES_DICT
)
from .constants import (
    CONFIG_PUBLIC_TEST_SEARCH_SEX_ONLY,
    DISCOVERY_CONFIG_TEST,
    CONFIG_PUBLIC_TEST_SEARCH_UNSET_FIELDS,
    DISCOVERY_CONFIG_EXTRA_PROPERTIES
)


class ScopedDiscoveryTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        # fallback on the node's discovery config
        cls.project_a = ch_m.Project.objects.create(
            title="Test project A",
            description="test description",
            discovery={},
        )
        # use provided dataset discovery config
        cls.dataset_a = ch_m.Dataset.objects.create(
            title="Dataset 1",
            description="Test dataset",
            data_use=ch_c.VALID_DATA_USE_1,
            project=cls.project_a,
            discovery=DISCOVERY_CONFIG_EXTRA_PROPERTIES,
        )

        # use provided project discovery config
        cls.project_b = ch_m.Project.objects.create(
            title="Test project B",
            description="test description",
            discovery=CONFIG_PUBLIC_TEST_SEARCH_SEX_ONLY,
        )
        # Should fallback on project's discovery config
        cls.dataset_b = ch_m.Dataset.objects.create(
            title="Dataset 2",
            description="Test dataset 2",
            data_use=ch_c.VALID_DATA_USE_1,
            project=cls.project_b,
            discovery={},
        )


class PublicSearchFieldsTest(APITestCase, ScopedDiscoveryTestCase):

    def setUp(self) -> None:
        # create 2 phenopackets for 2 individuals; each individual has 1 biosample;
        # one of phenopackets has 1 phenotypic feature and 1 disease
        self.individual_1 = ph_m.Individual.objects.create(**ph_c.VALID_INDIVIDUAL_1)
        self.metadata_1 = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_1)
        self.phenopacket_1 = ph_m.Phenopacket.objects.create(
            **ph_c.valid_phenopacket(subject=self.individual_1, meta_data=self.metadata_1),
            dataset=self.dataset_a
        )
        self.disease = ph_m.Disease.objects.create(**ph_c.VALID_DISEASE_1)
        self.biosample_1 = ph_m.Biosample.objects.create(**ph_c.valid_biosample_1(self.individual_1))
        self.phenotypic_feature = ph_m.PhenotypicFeature.objects.create(
            **ph_c.valid_phenotypic_feature(self.biosample_1, self.phenopacket_1)
        )
        self.phenopacket_1.biosamples.set([self.biosample_1])
        self.phenopacket_1.diseases.set([self.disease])

        # experiments
        self.instrument = exp_m.Instrument.objects.create(**exp_c.valid_instrument())
        self.experiment = exp_m.Experiment.objects.create(
            **exp_c.valid_experiment(self.biosample_1, self.instrument, dataset=self.dataset_a)
        )
        self.experiment_result = exp_m.ExperimentResult.objects.create(**exp_c.valid_experiment_result())
        self.experiment.experiment_results.set([self.experiment_result])

    def assert_response_section_fields(self, response_obj: dict, config: dict):
        self.assertSetEqual(
            set(field["id"] for section in response_obj["sections"] for field in section["fields"]),
            set(field for section in config["search"] for field in section["fields"])
        )

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_public_search_fields_configured(self):
        search_fields_url = reverse("public-search-fields")
        # SCOPE: whole node
        response = self.client.get(search_fields_url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_response_section_fields(response.json(), settings.CONFIG_PUBLIC)

        # SCOPE: project_a (same discovery as whole node)
        response_p_a = self.client.get(
            f"{search_fields_url}?project={str(self.project_a.identifier)}",
            content_type="application/json",
        )
        self.assertEqual(response_p_a.status_code, status.HTTP_200_OK)
        self.assert_response_section_fields(response_p_a.json(), settings.CONFIG_PUBLIC)

        # SCOPE: project_b (discovery search sex only)
        response_p_b = self.client.get(
            f"{search_fields_url}?project={str(self.project_b.identifier)}",
            content_type="application/json",
        )
        self.assertEqual(response_p_b.status_code, status.HTTP_200_OK)
        self.assert_response_section_fields(response_p_b.json(), CONFIG_PUBLIC_TEST_SEARCH_SEX_ONLY)

        # SCOPE: dataset_a (discovery with dataset specific extra_properties)
        response_d_a = self.client.get(
            f"{search_fields_url}?dataset={str(self.dataset_a.identifier)}",
            content_type="application/json",
        )
        self.assertEqual(response_d_a.status_code, status.HTTP_200_OK)
        self.assert_response_section_fields(response_d_a.json(), DISCOVERY_CONFIG_EXTRA_PROPERTIES)

        # SCOPE: non existing dataset
        response_d_invalid = self.client.get(
            f"{search_fields_url}?dataset={uuid.uuid4()}",
            content_type="application/json",
        )
        self.assertEqual(response_d_invalid.status_code, status.HTTP_404_NOT_FOUND)

        # SCOPE: non existing project
        response_p_invalid = self.client.get(
            f"{search_fields_url}?project={uuid.uuid4()}",
            content_type="application/json",
        )
        self.assertEqual(response_p_invalid.status_code, status.HTTP_404_NOT_FOUND)

        # SCOPE: dataset_b
        response_d_b = self.client.get(
            f"{search_fields_url}?dataset={self.dataset_b.identifier}",
            content_type="application/json",
        )
        self.assertEqual(response_d_b.status_code, status.HTTP_200_OK)
        # fallback on project's config, responses should be the same
        self.assertEqual(response_d_b.json(), response_p_b.json())

        # SCOPE: project_a + dataset_b (invalid)
        response_pd_invalid = self.client.get(
            f"{search_fields_url}?project={str(self.project_a.identifier)}&dataset={self.dataset_b.identifier}",
            content_type="application/json",
        )
        self.assertEqual(response_pd_invalid.status_code, status.HTTP_404_NOT_FOUND)

        # SCOPE: project_a + dataset_a (valid)
        response_pd_valid = self.client.get(
            f"{search_fields_url}?project={str(self.project_a.identifier)}&dataset={self.dataset_a.identifier}",
            content_type="application/json",
        )
        self.assertEqual(response_pd_valid.status_code, status.HTTP_200_OK)
        # same as dataset_a
        self.assertEqual(response_pd_valid.json(), response_d_a.json())

    @override_settings(CONFIG_PUBLIC={})
    def test_public_search_fields_not_configured(self):
        response = self.client.get(reverse("public-search-fields"), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response_obj = response.json()
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj, dres.NO_PUBLIC_FIELDS_CONFIGURED)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST_SEARCH_UNSET_FIELDS)
    def test_public_search_fields_missing_extra_properties(self):
        response = self.client.get(reverse("public-search-fields"), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_response_section_fields(response.json(), settings.CONFIG_PUBLIC)


class PublicOverviewTest(APITestCase, ScopedDiscoveryTestCase):

    def setUp(self) -> None:
        # individuals (count 8)
        individuals = {
            f"individual_{i}": ph_m.Individual.objects.create(**ind) for i, ind in enumerate(VALID_INDIVIDUALS, start=1)
        }
        # all individuals are in phenopackets that belong to dataset_a
        phenopackets = {
            f"phenopacket_{ind_label}": ph_m.Phenopacket.objects.create(
                **ph_c.valid_phenopacket(
                    subject=ind,
                    meta_data=ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_1),
                    id=f"phenopacket_{ind_label}"
                ),
                dataset=self.dataset_a
            ) for ind_label, ind in individuals.items()
        }
        # biosamples
        self.biosample_1 = ph_m.Biosample.objects.create(
            **ph_c.valid_biosample_1(individuals["individual_1"])
        )
        self.biosample_2 = ph_m.Biosample.objects.create(
            **ph_c.valid_biosample_2(individuals["individual_2"])
        )
        phenopackets["phenopacket_individual_1"].biosamples.set([self.biosample_1])
        phenopackets["phenopacket_individual_2"].biosamples.set([self.biosample_2])
        # experiments
        self.instrument = exp_m.Instrument.objects.create(**exp_c.valid_instrument())
        self.experiment = exp_m.Experiment.objects.create(
            **exp_c.valid_experiment(self.biosample_1, self.instrument, dataset=self.dataset_a)
        )
        self.experiment_result = exp_m.ExperimentResult.objects.create(**exp_c.valid_experiment_result())
        self.experiment.experiment_results.set([self.experiment_result])
        # make a copy and create experiment 2
        experiment_2 = deepcopy(exp_c.valid_experiment(self.biosample_2, self.instrument, dataset=self.dataset_a))
        experiment_2["id"] = "experiment:2"
        self.experiment = exp_m.Experiment.objects.create(**experiment_2)

        self.data_type_counts: dict[str, int] = {
            "individuals": ph_m.Individual.objects.all().count(),
            "biosamples": ph_m.Biosample.objects.all().count(),
            "experiments": exp_m.Experiment.objects.all().count()
        }

    def assert_counts_censored(self, overview_response: dict, discovery: dict):
        count_threshold = discovery["rules"]["count_threshold"]
        for data_type in self.data_type_counts.keys():
            response_count = overview_response["counts"][data_type]
            if response_count < count_threshold:
                self.assertEqual(response_count, 0)
            else:
                self.assertEqual(response_count, self.data_type_counts[data_type])

    def assert_scoped_fields(self, overview_response: dict, discovery: dict):
        self.assertSetEqual(
            set(field for field in overview_response["fields"].keys()),
            set(chart["field"] for section in discovery["overview"] for chart in section["charts"])
        )
    

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_overview(self):
        node_discovery = settings.CONFIG_PUBLIC
        public_overview_url = '/api/public_overview'
        # SCOPE: whole node
        response_whole = self.client.get(public_overview_url)
        response_whole_obj = response_whole.json()
        self.assertEqual(response_whole.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_whole_obj, dict)
        self.assert_counts_censored(response_whole_obj, node_discovery)
        self.assert_scoped_fields(response_whole_obj, node_discovery)

        # SCOPE: project_a (whole node fallback)
        response_p_a = self.client.get(f"{public_overview_url}?project={self.project_a.identifier}")
        self.assertEqual(response_p_a.status_code, status.HTTP_200_OK)
        self.assertEqual(response_p_a.json(), response_whole_obj)
        self.assert_counts_censored(response_whole_obj, node_discovery)
        self.assert_scoped_fields(response_whole_obj, node_discovery)

        # SCOPE: dataset_a
        response_d_a = self.client.get(f"{public_overview_url}?dataset={self.dataset_a.identifier}")
        self.assertEqual(response_d_a.status_code, status.HTTP_200_OK)
        self.assert_counts_censored(response_d_a.json(), self.dataset_a.discovery)
        self.assert_scoped_fields(response_d_a.json(), self.dataset_a.discovery)

        # SCOPE: project_b
        response_p_b = self.client.get(f"{public_overview_url}?project={self.project_b.identifier}")
        self.assertEqual(response_p_b.status_code, status.HTTP_200_OK)
        self.assert_counts_censored(response_p_b.json(), self.project_b.discovery)
        self.assert_scoped_fields(response_p_b.json(), self.project_b.discovery)

        # SCOPE: dataset_b (project_b fallback)
        response_d_b = self.client.get(f"{public_overview_url}?dataset={self.dataset_b.identifier}")
        self.assertEqual(response_d_b.status_code, status.HTTP_200_OK)
        self.assert_counts_censored(response_d_b.json(), self.project_b.discovery)
        self.assert_scoped_fields(response_d_b.json(), self.project_b.discovery)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
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
        self.assertEqual(response_obj, dres.NO_PUBLIC_DATA_AVAILABLE)


class PublicOverviewTest2(APITestCase):

    def setUp(self) -> None:
        # create only 2 individuals
        for ind in VALID_INDIVIDUALS[:2]:
            ph_m.Individual.objects.create(**ind)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_overview_response(self):
        # test overview response when individuals count < threshold
        response = self.client.get('/api/public_overview')
        response_obj = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj["counts"]["individuals"], 0)  # below count threshold

    @override_settings(CONFIG_PUBLIC={})
    def test_overview_response_no_config(self):
        # test overview response when individuals count < threshold
        response = self.client.get('/api/public_overview')
        response_obj = response.json()
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj, dres.NO_PUBLIC_DATA_AVAILABLE)


class PublicOverviewNotSupportedDataTypesListTest(APITestCase):
    # individuals (count 8)
    def setUp(self) -> None:
        # create individuals including those who have not accepted data types
        for ind in INDIVIDUALS_NOT_ACCEPTED_DATA_TYPES_LIST:
            ph_m.Individual.objects.create(**ind)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
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

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
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
            dats_content = json.loads(f.read())

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

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
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
        self.assertEqual(response_obj, dres.NO_PUBLIC_DATA_AVAILABLE)

class DiscoverySchemaTest(APITestCase):
    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discover_schema(self):
        response = self.client.get(reverse("discovery-schema"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), DISCOVERY_SCHEMA)
