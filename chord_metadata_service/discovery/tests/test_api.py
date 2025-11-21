import csv
import io
import json
from copy import deepcopy
import uuid

from bento_lib.discovery import DiscoveryConfig, RULES_NO_PERMISSIONS
from datetime import datetime
from django.conf import settings
from django.urls import reverse
from django.test import TestCase, override_settings
from rest_framework import status
from typing import Literal, TypedDict

from chord_metadata_service.authz.tests.helpers import DTAccessLevel, AuthzAPITestCase
from chord_metadata_service.chord import models as ch_m
from chord_metadata_service.chord.tests import constants as ch_c
from chord_metadata_service.discovery import responses as dres
from chord_metadata_service.discovery.schemas import DISCOVERY_SCHEMA
from chord_metadata_service.patients import models as pa_m
from chord_metadata_service.phenopackets import models as ph_m
from chord_metadata_service.phenopackets.tests import constants as ph_c
from chord_metadata_service.experiments import models as exp_m
from chord_metadata_service.experiments.tests import constants as exp_c

from chord_metadata_service.restapi.pagination import DEFAULT_PAGE_SIZE
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


def _iso(ts: datetime) -> str:
    return ts.isoformat().replace("+00:00", "Z")


class ScopedDiscoveryTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        # fallback on the node's discovery config
        cls.project_a = ch_m.Project.objects.create(
            title="Test project A",
            description="test description",
            discovery=None,
        )
        cls.id_proj_a = cls.project_a.identifier
        # use provided dataset discovery config
        cls.dataset_a = ch_m.Dataset.objects.create(
            title="Dataset 1",
            description="Test dataset",
            data_use=ch_c.VALID_DATA_USE_1,
            project=cls.project_a,
            discovery=DISCOVERY_CONFIG_EXTRA_PROPERTIES,
        )
        cls.id_ds_a = cls.dataset_a.identifier

        # use provided project discovery config
        cls.project_b = ch_m.Project.objects.create(
            title="Test project B",
            description="test description",
            discovery=CONFIG_PUBLIC_TEST_SEARCH_SEX_ONLY,
        )
        cls.id_proj_b = cls.project_b.identifier
        # Should fallback on project's discovery config
        cls.dataset_b = ch_m.Dataset.objects.create(
            title="Dataset 2",
            description="Test dataset 2",
            data_use=ch_c.VALID_DATA_USE_1,
            project=cls.project_b,
            discovery=None,
        )
        cls.id_ds_b = cls.dataset_b.identifier


TestDiscoveryConfigKey = Literal["public", "sex_only", "extra_props", "none"]


class TestDiscoveryConfigsDict(TypedDict):
    public: DiscoveryConfig
    sex_only: DiscoveryConfig
    extra_props: DiscoveryConfig
    none: None


class DiscoverySearchFieldsTest(AuthzAPITestCase, ScopedDiscoveryTestCase):

    def setUp(self) -> None:
        # create 2 phenopackets for 2 individuals; each individual has 1 biosample;
        # one of phenopackets has 1 phenotypic feature and 1 disease
        self.individual_1 = pa_m.Individual.objects.create(**ph_c.VALID_INDIVIDUAL_1)
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

    @staticmethod
    def discovery_test_configs() -> TestDiscoveryConfigsDict:
        return {
            "public": settings.CONFIG_PUBLIC,
            "sex_only": CONFIG_PUBLIC_TEST_SEARCH_SEX_ONLY,
            "extra_props": DISCOVERY_CONFIG_EXTRA_PROPERTIES,
            "none": None,
        }

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discovery_search_fields_configured(self):
        search_fields_url = reverse("discovery-search-fields")

        subtest_params: list[tuple[DTAccessLevel, str, int, TestDiscoveryConfigKey | dict]] = [
            # SCOPE: whole node
            ("counts", "", status.HTTP_200_OK, "public"),
            # SCOPE: project_a (same discovery as whole node)
            ("counts", f"?project={str(self.id_proj_a)}", status.HTTP_200_OK, "public"),
            # SCOPE: project_b (discovery search sex only)
            ("counts", f"?project={str(self.id_proj_b)}", status.HTTP_200_OK, "sex_only"),
            # SCOPE: dataset_a (discovery with dataset specific extra_properties)
            ("counts", f"?dataset={str(self.id_ds_a)}", status.HTTP_200_OK, "extra_props"),
            # SCOPE: non-existant dataset
            ("counts", f"?dataset={uuid.uuid4()}", status.HTTP_404_NOT_FOUND, "none"),
            # SCOPE: non-existant project
            ("counts", f"?project={uuid.uuid4()}", status.HTTP_404_NOT_FOUND, "none"),
            # SCOPE: dataset_b
            #  - fallback on project's config, responses should be the same
            #  - see above - CONFIG_PUBLIC_TEST_SEARCH_SEX_ONLY
            ("counts", f"?dataset={self.id_ds_b}", status.HTTP_200_OK, "sex_only"),
            # SCOPE: project_a + dataset_b (invalid)
            ("counts", f"?project={str(self.id_proj_a)}&dataset={self.id_ds_b}", status.HTTP_404_NOT_FOUND, "none"),
            # SCOPE: project_a + dataset_a (valid)
            #  - same as dataset_a - DISCOVERY_CONFIG_EXTRA_PROPERTIES
            ("counts", f"?project={str(self.id_proj_a)}&dataset={self.id_ds_a}", status.HTTP_200_OK, "extra_props"),
            # invalid UUID for project
            ("counts", "?project=not-a-uuid", status.HTTP_404_NOT_FOUND, "none"),
            # invalid UUID for dataset
            ("counts", "?dataset=not-a-uuid", status.HTTP_404_NOT_FOUND, "none"),
            # ------------------------------------------ lacking permissions ------------------------------------------
            #  - no sections with permissions -> a response with no sections available
            ("none", "", status.HTTP_200_OK, {"sections": []}),
            ("bool", f"?project={str(self.id_proj_a)}", status.HTTP_200_OK, {"sections": []}),
        ]

        # use key aliases for configs to make subtest failure output more readable
        dtc = self.discovery_test_configs()  # to get injected CONFIG_PUBLIC, need to calculate this in-test

        for params in subtest_params:
            with self.subTest(params=params):
                level, qp, expected_status_code, config_key_or_res = params
                res = self.dt_get(level, f"{search_fields_url}{qp}")
                self.assertEqual(res.status_code, expected_status_code)

                if isinstance(config_key_or_res, dict):
                    self.assertDictEqual(res.json(), config_key_or_res)
                else:
                    expected_body_config: DiscoveryConfig | None = dtc[config_key_or_res]
                    if expected_body_config is not None:
                        self.assert_response_section_fields(res.json(), expected_body_config.model_dump(mode="json"))

    @override_settings(CONFIG_PUBLIC=DiscoveryConfig())
    def test_discovery_search_fields_not_configured(self):
        response = self.dt_authz_counts_get(reverse("discovery-search-fields"), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response_obj = response.json()
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj, dres.NO_PUBLIC_FIELDS_CONFIGURED)

    @override_settings(CONFIG_PUBLIC=CONFIG_PUBLIC_TEST_SEARCH_UNSET_FIELDS)
    def test_discovery_search_fields_missing_extra_properties(self):
        response = self.dt_authz_counts_get(reverse("discovery-search-fields"), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_response_section_fields(response.json(), settings.CONFIG_PUBLIC.model_dump(mode="json"))


class DiscoveryOverviewTest(AuthzAPITestCase, ScopedDiscoveryTestCase):

    def setUp(self) -> None:
        self.url = '/api/discovery'

        # individuals (count 8)
        individuals = {
            f"individual_{i}": pa_m.Individual.objects.create(**ind) for i, ind in enumerate(VALID_INDIVIDUALS, start=1)
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

        self.data_type_counts_ds_a: dict[str, int] = {
            "individual": pa_m.Individual.objects.all().count(),
            "biosample": ph_m.Biosample.objects.all().count(),
            "experiment": exp_m.Experiment.objects.all().count(),  # two - below censor threshold for counts-access
        }

        self.data_type_counts_ds_b: dict[str, int] = {
            "individual": 0,
            "biosample": 0,
            "experiment": 0,
        }

    def assert_counts_censored(self, overview_response: dict, discovery: DiscoveryConfig, dts: dict[str, int]):
        count_threshold = discovery.rules.count_threshold
        for data_type in dts.keys():
            response_count = overview_response["counts"][data_type]
            if dts[data_type] <= count_threshold:
                self.assertEqual(response_count, 0)
            else:
                self.assertEqual(response_count, dts[data_type])

    def assert_bools_censored(self, overview_response: dict, discovery: DiscoveryConfig, dts: dict[str, int]):
        count_threshold = discovery.rules.count_threshold
        for data_type in dts.keys():
            response_val = overview_response["counts"][data_type]
            # sub-threshold --> false response, above-threshold --> true response
            self.assertEqual(response_val, dts[data_type] > count_threshold)

    def assert_counts_not_censored(self, overview_response: dict, dts: dict[str, int]):
        for data_type in dts.keys():
            response_count = overview_response["counts"][data_type]
            self.assertEqual(response_count, dts[data_type])

    def assert_scoped_fields(
        self, overview_response: dict, discovery: DiscoveryConfig, expected_fields: set[str] | None = None
    ):
        response_fields = set(field for field in overview_response["fields"].keys())
        chart_fields = set(discovery.get_chart_field_ids()) if expected_fields is None else expected_fields
        self.assertSetEqual(response_fields, chart_fields)

    def test_empty_discovery(self):
        res = self.dt_authz_full_get(self.url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(res.json(), {"message": "No public data available."})

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_overview(self):
        node_discovery = settings.CONFIG_PUBLIC

        subtest_params: list[tuple[str, int, DiscoveryConfig | None, dict[str, int] | None]] = [
            # --- VALID ---
            # SCOPE: whole node
            ("", status.HTTP_200_OK, node_discovery, self.data_type_counts_ds_a),  # everything is in dataset a
            # SCOPE: project_a (whole node fallback)
            (f"?project={self.id_proj_a}", status.HTTP_200_OK, node_discovery, self.data_type_counts_ds_a),
            # SCOPE: dataset_a
            (
                f"?dataset={self.id_ds_a}",
                status.HTTP_200_OK,
                self.dataset_a.discovery,
                self.data_type_counts_ds_a,
            ),
            # SCOPE: project_b
            (
                f"?project={self.id_proj_b}",
                status.HTTP_200_OK,
                self.project_b.discovery,
                self.data_type_counts_ds_b,
            ),
            # SCOPE: dataset_b (project_b fallback)
            (
                f"?dataset={self.id_ds_b}",
                status.HTTP_200_OK,
                self.project_b.discovery,
                self.data_type_counts_ds_b,
            ),
            # --- INVALID ---
            # invalid UUID for project (not found; IDs are not of this format)
            ("?project=not-a-uuid", status.HTTP_404_NOT_FOUND, None, None),
            # invalid UUID for dataset (not found; IDs are not of this format)
            ("?dataset=not-a-uuid", status.HTTP_404_NOT_FOUND, None, None),
        ]

        for i, params in enumerate(subtest_params):
            with self.subTest(params=(i, *params)):
                qp, expected_status_code, discovery, dts = params
                url = f"{self.url}{qp}"

                if discovery:
                    # none and bool-level permissions should get forbidden errors for overview, currently
                    res = self.dt_get("none", url)
                    self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

                # with bool permissions, we should get the expected status code + (if success) True/False
                #  based on censored count
                res = self.dt_get("bool", url)
                self.assertEqual(res.status_code, expected_status_code)

                if discovery:
                    res_json = res.json()
                    self.assertIsInstance(res_json, dict)
                    self.assert_bools_censored(res_json, discovery, dts)
                    # scoped fields but without any data right now for bools:
                    #   no fields have counts permissions, so we don't get any fields back
                    self.assert_scoped_fields(res_json, discovery, expected_fields=set())

                # with counts permissions, we should get the expected status code + (if success) censored counts, but we
                # may be missing some fields

                res = self.dt_get("counts", url)
                self.assertEqual(res.status_code, expected_status_code)

                if discovery:
                    res_json = res.json()
                    self.assertIsInstance(res_json, dict)
                    self.assert_counts_censored(res_json, discovery, dts)

                    expected_fields = set(discovery.get_chart_field_ids())
                    if not res_json["counts"].get("biosample"):
                        # remove biosample fields from expected response if biosamples censored
                        expected_fields -= {"tissues", "diagnostic_markers"}

                    self.assert_scoped_fields(res_json, discovery)

                # with full permissions, we should get the expected status code + (if success) uncensored counts plus
                # all scoped field responses

                res = self.dt_get("full", url)
                self.assertEqual(res.status_code, expected_status_code)

                if discovery:
                    res_json = res.json()
                    self.assertIsInstance(res_json, dict)
                    self.assert_counts_not_censored(res_json, dts)
                    self.assert_scoped_fields(res_json, discovery)  # should have all fields, even ones with 0-counts

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_overview_project_dataset(self):
        # SCOPE: project_a + dataset_a
        response = self.dt_authz_counts_get(f"{self.url}?project={self.id_proj_a}&dataset={self.id_ds_a}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res_json = response.json()
        discovery = self.dataset_a.discovery
        # we only have two biosamples, so any fields involving them (tissues, diagnostic_markers) or experiments
        # (theoretically) gets censored.
        self.assert_scoped_fields(
            res_json,
            discovery,
            expected_fields=set(discovery.get_chart_field_ids()) - {"tissues", "diagnostic_markers"},
        )
        # because we only have two biosamples, counts of biosamples + entities nested under (experiments)
        self.assertDictEqual(res_json["counts"], {
            "phenopacket": 8,
            "individual": 8,
            "biosample": 0,
            "experiment": 0,
            "experiment_result": 0,
        })

        # SCOPE: project_a + dataset_b (invalid)
        response_invalid = self.dt_authz_counts_get(f"{self.url}?project={self.id_proj_a}&dataset={self.id_ds_b}")
        self.assertEqual(response_invalid.status_code, status.HTTP_404_NOT_FOUND)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
    def test_overview_bins(self):
        # test that there is the correct number of data entries for number
        # histograms, vs. number of bins
        response = self.dt_authz_counts_get(self.url)
        response_obj = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(
            # 1 more bin than intervals expected: e.g. for config.bins = [2, 3, 4],
            # we expect data entries for ≤2, [2 3), [3 4), ≥4
            len(response_obj["fields"]["lab_test_result_value"]["definition"]["config"]["bins"]) + 1,
            len(response_obj["fields"]["lab_test_result_value"]["data"]),
        )

    @override_settings(CONFIG_PUBLIC=DiscoveryConfig())
    def test_overview_no_config(self):
        response = self.dt_authz_counts_get(self.url)
        response_obj = response.json()
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj, dres.NO_PUBLIC_DATA_AVAILABLE)


class DiscoveryOverviewTest2(AuthzAPITestCase):

    def setUp(self) -> None:
        self.url = '/api/discovery'
        # create only 2 individuals
        for i, ind in enumerate(VALID_INDIVIDUALS[:2]):
            ind_obj = pa_m.Individual.objects.create(**ind)
            md = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_1)
            ph_m.Phenopacket.objects.create(id=f"phe-{i}", subject=ind_obj, meta_data=md)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_overview_response(self):
        # test overview response when individuals count < threshold
        response = self.dt_authz_counts_get(self.url)
        response_obj = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj["counts"]["individual"], 0)  # below count threshold

    @override_settings(CONFIG_PUBLIC=DiscoveryConfig())
    def test_overview_response_no_config(self):
        # test overview response when individuals count < threshold
        response = self.dt_authz_counts_get(self.url)
        response_obj = response.json()
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj, dres.NO_PUBLIC_DATA_AVAILABLE)


class DiscoveryOverviewInvalidExtraPropsDataTypesListTest(AuthzAPITestCase):
    # individuals (count 8)
    def setUp(self) -> None:
        # create individuals including those who have not accepted data types
        for i, ind in enumerate(INDIVIDUALS_NOT_ACCEPTED_DATA_TYPES_LIST):
            ind_obj = ph_m.Individual.objects.create(**ind)
            md = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_1)
            ph_m.Phenopacket.objects.create(id=f"phe-{i}", subject=ind_obj, meta_data=md)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
    def test_overview_response(self):
        # test overview response with passing TypeError exception

        response = self.dt_authz_counts_get('/api/discovery')
        response_obj = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_obj, dict)

        self.assertEqual(response_obj["counts"]["phenopacket"], len(INDIVIDUALS_NOT_ACCEPTED_DATA_TYPES_DICT))  # 8
        self.assertEqual(response_obj["counts"]["individual"], len(INDIVIDUALS_NOT_ACCEPTED_DATA_TYPES_DICT))  # 8

        # the field name is present, but the keys are not (except 'missing')
        self.assertIn("baseline_creatinine", response_obj["fields"])
        self.assertIn("missing", response_obj["fields"]["baseline_creatinine"]["data"][-1]["label"])
        self.assertEqual(8, response_obj["fields"]["baseline_creatinine"]["data"][-1]["value"])
        # if we add support for an array values for the discovery fields response
        # then this assertion will fail, so far there is no support for it
        self.assertNotIn(
            100,
            [data["value"] for data in response_obj["fields"]["baseline_creatinine"]["data"]])


class DiscoveryOverviewInvalidExtraPropsDataTypesDictTest(AuthzAPITestCase):
    # phenopackets+individuals (count 8)
    # used to be individuals only, but with the new discovery endpoint we switched to being phenopackets-centric
    def setUp(self) -> None:
        # create individuals including those who have invalid extra properties types
        for i, ind in enumerate(INDIVIDUALS_NOT_ACCEPTED_DATA_TYPES_DICT):
            ind_obj = ph_m.Individual.objects.create(**ind)
            md = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_1)
            ph_m.Phenopacket.objects.create(id=f"phe-{i}", subject=ind_obj, meta_data=md)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_EXTRA_PROPERTIES)
    def test_discovery_response(self):
        # test overview response with passing TypeError exception
        response = self.dt_authz_counts_get('/api/discovery')
        response_obj = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_obj, dict)

        self.assertEqual(response_obj["counts"]["phenopacket"], len(INDIVIDUALS_NOT_ACCEPTED_DATA_TYPES_DICT))  # 8
        self.assertEqual(response_obj["counts"]["individual"], len(INDIVIDUALS_NOT_ACCEPTED_DATA_TYPES_DICT))  # 8

        # the field name is present, but the keys are not since they're of the wrong type; only 'missing'
        self.assertIn("baseline_creatinine", response_obj["fields"])
        self.assertIn("missing", response_obj["fields"]["baseline_creatinine"]["data"][-1]["label"])
        self.assertEqual(8, response_obj["fields"]["baseline_creatinine"]["data"][-1]["value"])


def make_two_individuals_with_phenopackets() -> tuple[str, str, list[pa_m.Individual], list[ph_m.Phenopacket]]:
    # create project + dataset
    p = ch_m.Project.objects.create(**ch_c.VALID_PROJECT_1)
    d = ch_m.Dataset.objects.create(**ch_c.valid_dataset_1(p))

    individuals = []
    phenopackets = []

    # create only 2 individuals
    for i, ind in enumerate(VALID_INDIVIDUALS[:2]):
        ind_obj = pa_m.Individual.objects.create(**ind)
        individuals.append(ind_obj)
        bios = []
        if i == 0:
            bios.append(ph_m.Biosample.objects.create(**ph_c.valid_biosample_1(ind_obj)))
        elif i == 1:
            bios.append(ph_m.Biosample.objects.create(**ph_c.valid_biosample_2(ind_obj)))

        md = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_1)
        phe_obj = ph_m.Phenopacket.objects.create(id=f"phe-{i}", dataset=d, subject=ind_obj, meta_data=md)
        phe_obj.biosamples.set(bios)
        phe_obj.save()

        if i == 0:
            # set up one phenotypic feature and one disease for the first phenopacket
            ph_m.PhenotypicFeature.objects.create(**ph_c.valid_phenotypic_feature(phenopacket=phe_obj))

            disease = ph_m.Disease.objects.create(**ph_c.VALID_DISEASE_1)
            phe_obj.diseases.set([disease])

        phenopackets.append(phe_obj)

    return str(p.identifier), str(d.identifier), individuals, phenopackets


class DiscoveryMatchesTest(AuthzAPITestCase):
    def setUp(self):
        self.url = reverse("discovery-matches")
        self.maxDiff = None

        self.csv_disease = "Spinocerebellar ataxia 1 (P25Y3M2D)"
        self.csv_cr_sub = "David Lougheed,David Lougheed"

    @staticmethod
    def _rn_newline(x: str) -> str:
        return x.replace("\r\n", "\n").replace("\n", "\r\n")

    def test_empty_discovery(self):
        res = self.dt_authz_full_get(self.url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(res.json(), {"message": "No public data available."})

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_empty_matches(self):
        res = self.dt_authz_full_get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertDictEqual(res.json(), {
            "results_entity": "phenopacket",
            "results": [],
            "pagination": {
                "page": 0,
                "page_size": 25,
                "total": 0,
            },
        })

    def assertErrorRes(
        self, res, error_text: str, is_csv_response: bool = False, code: int = status.HTTP_400_BAD_REQUEST, **kwargs
    ):
        self.assertEqual(res.status_code, code)

        if is_csv_response:
            r = csv.DictReader(io.StringIO(res.content.decode("utf-8")))
            res_dict = next(r)
            self.assertDictEqual(res_dict, {k: str(v) for k, v in {
                "code": code,
                "message": "Bad Request",
                "errors": json.dumps([{"message": error_text}], indent=None).strip(),
                "timestamp": res_dict["timestamp"],
                **kwargs,
            }.items()})
        else:
            res_json = res.json()
            self.assertDictEqual(res_json, {
                "code": code,
                "message": "Bad Request",
                "errors": [{"message": error_text}],
                "timestamp": res_json["timestamp"],
                **kwargs,
            })

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_bad_pagination_non_int_page(self):
        make_two_individuals_with_phenopackets()
        res = self.dt_authz_full_get(f"{self.url}?_page_size=1&_page=one")
        self.assertErrorRes(res, "bad page")

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_bad_pagination_non_int_page_size(self):
        make_two_individuals_with_phenopackets()
        res = self.dt_authz_full_get(f"{self.url}?_page_size=one&_page=1")
        self.assertErrorRes(res, "bad page size")

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_bad_pagination_too_large_page(self):
        make_two_individuals_with_phenopackets()
        res = self.dt_authz_full_get(f"{self.url}?_page_size=1&_page=2")
        self.assertErrorRes(res, "bad page")

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_bad_response_type(self):
        make_two_individuals_with_phenopackets()
        res = self.dt_authz_full_get(f"{self.url}?_format=bad")
        self.assertErrorRes(res, "bad response format")

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_response_type_mismatch(self):
        make_two_individuals_with_phenopackets()
        for fmt, accept in [("csv", "application/json"), ("json", "text/csv")]:
            with self.subTest(params=(fmt, accept)):
                res = self.dt_authz_full_get(f"{self.url}?_format={fmt}", headers={"Accept": accept})
                self.assertErrorRes(
                    res,
                    "mismatch between accepted and specified response formats",
                    is_csv_response=accept.endswith("csv"),
                    code=status.HTTP_406_NOT_ACCEPTABLE,
                    message="Not Acceptable",
                )

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_a_few_json_responses_phenopackets(self):
        p, d, individuals, phenopackets = make_two_individuals_with_phenopackets()

        full_res = {
            "results_entity": "phenopacket",
            "results": [
                {
                    "id": "phe-0",
                    "subject": str(individuals[0].id),
                    "biosamples": [{
                        "id": str(phenopackets[0].biosamples.first().id),
                        "individual_id": str(phenopackets[0].subject_id),
                        "experiments": [],
                        "phenopacket": str(phenopackets[0].id),
                    }],
                    "project": p,
                    "dataset": d,
                },
                {
                    "id": "phe-1",
                    "subject": str(individuals[1].id),
                    "biosamples": [{
                        "id": str(phenopackets[1].biosamples.first().id),
                        "individual_id": str(phenopackets[1].subject_id),
                        "experiments": [],
                        "phenopacket": str(phenopackets[1].id),
                    }],
                    "project": p,
                    "dataset": d,
                },
            ],
            "pagination": {
                "page": 0,
                "page_size": 25,
                "total": 2,
            },
        }

        full_response_page_sizes = [None, 2, 25, 0]  # page sizes

        for page_size in full_response_page_sizes:
            with self.subTest(params=(page_size,)):
                res = self.dt_authz_full_get(
                    f"{self.url}?_page_size={page_size}" if page_size is not None else self.url
                )
                self.assertEqual(res.status_code, status.HTTP_200_OK)
                expected_res = deepcopy(full_res)
                expected_res["pagination"]["page_size"] = page_size if page_size is not None else DEFAULT_PAGE_SIZE
                self.assertDictEqual(res.json(), expected_res)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_a_few_json_responses_phenopackets_pagination(self):
        p, d, individuals, phenopackets = make_two_individuals_with_phenopackets()

        res = self.dt_authz_full_get(f"{self.url}?_page_size=1&_page=1")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertDictEqual(res.json(), {
            "results_entity": "phenopacket",
            "results": [
                {
                    "id": "phe-1",
                    "subject": str(individuals[1].id),
                    "biosamples": [{
                        "id": str(phenopackets[1].biosamples.first().id),
                        "individual_id": str(phenopackets[1].subject_id),
                        "experiments": [],
                        "phenopacket": str(phenopackets[1].id),
                    }],
                    "project": p,
                    "dataset": d,
                },
            ],
            "pagination": {
                "page": 1,
                "page_size": 1,
                "total": 2,
            },
        })

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_a_few_json_responses_individuals(self):
        p, d, individuals, phenopackets = make_two_individuals_with_phenopackets()

        res = self.dt_authz_full_get(f"{self.url}?_entity=individual")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertDictEqual(res.json(), {
            "results_entity": "individual",
            "results": [
                {
                    "id": VALID_INDIVIDUALS[1]["id"],
                    "phenopackets": [
                        {
                            "biosamples": [{
                                "id": str(phenopackets[1].biosamples.first().id),
                                "individual_id": str(phenopackets[1].subject_id),
                                "experiments": [],
                                "phenopacket": str(phenopackets[1].id),
                            }],
                            "id": "phe-1",
                            "subject": str(individuals[1].id),
                        },
                    ],
                    "project": p,
                    "dataset": d,
                },
                {
                    "id": VALID_INDIVIDUALS[0]["id"],
                    "phenopackets": [
                        {
                            "biosamples": [{
                                "id": str(phenopackets[0].biosamples.first().id),
                                "individual_id": str(phenopackets[0].subject_id),
                                "experiments": [],
                                "phenopacket": str(phenopackets[0].id),
                            }],
                            "id": "phe-0",
                            "subject": str(individuals[0].id),
                        },
                    ],
                    "project": p,
                    "dataset": d,
                },
            ],
            "pagination": {
                "page": 0,
                "page_size": 25,
                "total": 2,
            },
        })

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_empty_json_responses_experiments(self):  # if we add experiments/results, "empty" --> "a_few"
        make_two_individuals_with_phenopackets()
        res = self.dt_authz_full_get(f"{self.url}?_entity=experiment")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertDictEqual(res.json(), {
            "results_entity": "experiment",
            "results": [],
            "pagination": {
                "page": 0,
                "page_size": 25,
                "total": 0,
            },
        })

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_empty_json_responses_experiment_results(self):  # if we add experiments/results, "empty" --> "a_few"
        make_two_individuals_with_phenopackets()
        res = self.dt_authz_full_get(f"{self.url}?_entity=experiment_result")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertDictEqual(res.json(), {
            "results_entity": "experiment_result",
            "results": [],
            "pagination": {
                "page": 0,
                "page_size": 25,
                "total": 0,
            },
        })

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_a_few_csv_responses_phenopackets(self):
        p, d, _individuals, _phenopackets = make_two_individuals_with_phenopackets()
        res = self.dt_authz_full_get(f"{self.url}?_format=csv")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        sp = "Homo sapiens"
        self.assertEqual(
            res.content.decode("utf-8"),
            self._rn_newline(
                f"""Id,Subject id,Subject sex,Subject taxonomy,Biosamples,Diseases,Created by,Submitted by,Dataset
phe-0,ind:NA19648,FEMALE,{sp},katsu.biosample_id:1 [wall of urinary bladder],{self.csv_disease},{self.csv_cr_sub},{d}
phe-1,ind:HG00096,MALE,{sp},biosample_id:2 [urinary bladder],,{self.csv_cr_sub},{d}
"""
            )  # CSVs use \r\n line endings here
        )

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_a_few_csv_responses_phenopackets_pagination(self):
        p, d, _individuals, _phenopackets = make_two_individuals_with_phenopackets()
        # also (at the same time) test that accept works with unspecified format:
        res = self.dt_authz_full_get(f"{self.url}?_page_size=1&_page=1", headers={"Accept": "text/csv"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.content.decode("utf-8"),
            self._rn_newline(
                f"""Id,Subject id,Subject sex,Subject taxonomy,Biosamples,Diseases,Created by,Submitted by,Dataset
phe-1,ind:HG00096,MALE,Homo sapiens,biosample_id:2 [urinary bladder],,{self.csv_cr_sub},{d}
"""
            )  # CSVs use \r\n line endings here
        )

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_a_few_csv_responses_individuals(self):
        _p, _d, [i0, i1], _phenopackets = make_two_individuals_with_phenopackets()

        res = self.dt_authz_full_get(f"{self.url}?_format=csv&_entity=individual")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.content.decode("utf-8"),
            self._rn_newline(
                f"""Id,Sex,Date of birth,Taxonomy,Karyotypic sex,Age,Diseases,Created,Updated
ind:HG00096,MALE,1924-03-29,Homo sapiens,XY,P97Y,,{_iso(i1.created)},{_iso(i1.updated)}
ind:NA19648,FEMALE,1993-10-04,Homo sapiens,XX,P28Y,{self.csv_disease},{_iso(i0.created)},{_iso(i0.updated)}
"""
            )  # CSVs use \r\n line endings here
        )

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_empty_csv_responses_biosamples(self):  # if we add experiments/results, "empty" --> "a_few"
        _p, _d, _, phenopackets = make_two_individuals_with_phenopackets()

        hdr = (
            "Id,Description,Sampled tissue,Time of collection,Histological diagnosis,Extra properties,Created,Updated,"
            "Individual"
        )

        bs0 = phenopackets[0].biosamples.first()
        bs1 = phenopackets[1].biosamples.first()
        cruds0 = f"{_iso(bs0.created)},{_iso(bs0.updated)},{phenopackets[0].subject.id}"
        cruds1 = f"{_iso(bs1.created)},{_iso(bs1.updated)},{phenopackets[1].subject.id}"

        res = self.dt_authz_full_get(f"{self.url}?_format=csv&_entity=biosample")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.content.decode("utf-8"),
            self._rn_newline(
                f"""{hdr}
{bs1.id},This is a test biosample.,urinary bladder,P45Y,Infiltrating Urothelial Carcinoma,Material: NA,{cruds1}
{bs0.id},This is a test biosample.,wall of urinary bladder,P45Y,Infiltrating Urothelial Carcinoma,Material: NA,{cruds0}
"""
            )  # CSVs use \r\n line endings here
        )

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_empty_csv_responses_experiments(self):  # if we add experiments/results, "empty" --> "a_few"
        make_two_individuals_with_phenopackets()

        hdr = (
            "Id,Study type,Experiment type,Molecule,Library strategy,Library source,Library selection,Library layout,"
            "Created,Updated,Biosample,Individual"
        )

        # Empty CSV
        res = self.dt_authz_full_get(f"{self.url}?_format=csv&_entity=experiment")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.content.decode("utf-8"),
            self._rn_newline(
                f"""{hdr}
"""
            )  # CSVs use \r\n line endings here
        )

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_a_few_csv_responses_experiment_results(self):
        make_two_individuals_with_phenopackets()

        hdr = (
            "Id,Description,Filename,Url,Genome assembly id,File format,Data output type,Usage,Creation date,Created by"
        )

        # Empty CSV
        res = self.dt_authz_full_get(f"{self.url}?_format=csv&_entity=experiment_result")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.content.decode("utf-8"),
            self._rn_newline(
                f"""{hdr}
"""
            )  # CSVs use \r\n line endings here
        )


class DiscoveryUIHintsTest(AuthzAPITestCase):
    def setUp(self):
        self.url = reverse("discovery-ui-hints")

    @override_settings(CONFIG_PUBLIC=DiscoveryConfig())
    def test_empty_discovery(self):
        res = self.dt_authz_counts_get(self.url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_bad_scope(self):
        res = self.dt_authz_counts_get(f"{self.url}?project=does-not-exist")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(res.json()["message"], "Not Found")

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_empty_entities_with_data(self):
        res = self.dt_authz_counts_get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertListEqual(res.json()["entities_with_data"], [])

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_few_entities(self):
        # create only 2 individuals
        make_two_individuals_with_phenopackets()

        # -------------------------------------------------------------------------------

        # With bool/counts, this is below the censorship threshold, so we get no entities with data.
        # With full data access, we can learn we have phenopackets/individuals.

        res = self.dt_authz_bool_get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertListEqual(res.json()["entities_with_data"], [])

        res = self.dt_authz_counts_get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertListEqual(res.json()["entities_with_data"], [])

        res = self.dt_authz_full_get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertSetEqual(set(res.json()["entities_with_data"]), {"phenopacket", "individual", "biosample"})

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_many_entities(self):
        for i, ind in enumerate(VALID_INDIVIDUALS):
            ind_obj = pa_m.Individual.objects.create(**ind)
            md = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_1)
            ph_m.Phenopacket.objects.create(id=f"phe-{i}", subject=ind_obj, meta_data=md)

        # -------------------------------------------------------------------------------

        # Since we have many entities (and are now above the censorship threshold), we should now get entities_with_data
        # being "complete" in all authorization cases:

        res = self.dt_authz_bool_get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertSetEqual(set(res.json()["entities_with_data"]), {"phenopacket", "individual"})

        res = self.dt_authz_counts_get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertSetEqual(set(res.json()["entities_with_data"]), {"phenopacket", "individual"})

        res = self.dt_authz_full_get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertSetEqual(set(res.json()["entities_with_data"]), {"phenopacket", "individual"})


class DiscoverySchemaTest(AuthzAPITestCase):
    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discover_schema(self):
        response = self.dt_authz_counts_get(reverse("discovery-schema"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), DISCOVERY_SCHEMA)


class DiscoveryRulesTest(AuthzAPITestCase, ScopedDiscoveryTestCase):
    def setUp(self):
        self.url = reverse("discovery-rules")

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_discovery_rules(self):
        # Node scope
        # SCOPE: whole node
        response = self.dt_authz_counts_get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), DISCOVERY_CONFIG_TEST.rules.model_dump(mode="json"))

        # PROJECTS
        response_p_a = self.dt_authz_counts_get(f"{self.url}?project={self.id_proj_a}")
        self.assertEqual(response_p_a.status_code, status.HTTP_200_OK)
        # node discovery fallback:
        self.assertEqual(response_p_a.json(), DISCOVERY_CONFIG_TEST.rules.model_dump(mode="json"))

        response_p_b = self.dt_authz_counts_get(f"{self.url}?project={self.id_proj_b}")
        self.assertEqual(response_p_b.status_code, status.HTTP_200_OK)
        self.assertEqual(response_p_b.json(), self.project_b.discovery.rules.model_dump(mode="json"))

        # Dataset scope
        response_d_a = self.dt_authz_counts_get(f"{self.url}?dataset={self.id_ds_a}")
        self.assertEqual(response_d_a.status_code, status.HTTP_200_OK)
        self.assertEqual(response_d_a.json(), self.dataset_a.discovery.rules.model_dump(mode="json"))

        response_d_b = self.dt_authz_counts_get(f"{self.url}?dataset={self.id_ds_b}")
        self.assertEqual(response_d_b.status_code, status.HTTP_200_OK)
        self.assertEqual(response_d_b.json(), self.project_b.discovery.rules.model_dump(mode="json"))

    @override_settings(CONFIG_PUBLIC=DiscoveryConfig())
    def test_discovery_exp_1(self):
        # Node scope not configured
        response = self.dt_authz_none_get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # no permissions -> rules for no permissions
        self.assertEqual(response.json(), RULES_NO_PERMISSIONS.model_dump(mode="json"))

    @override_settings(CONFIG_PUBLIC=DiscoveryConfig())
    def test_discovery_exp_2(self):
        # Node scope not configured
        response = self.dt_authz_counts_get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # no config -> rules for no permissions
        self.assertEqual(response.json(), RULES_NO_PERMISSIONS.model_dump(mode="json"))

        response_exp = self.dt_authz_counts_get(f"{self.url}?project={self.id_proj_a}&dataset={self.id_ds_b}")
        self.assertEqual(response_exp.status_code, status.HTTP_404_NOT_FOUND)
