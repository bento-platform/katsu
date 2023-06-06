import json
import uuid

from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets.models import Biosample, MetaData, Phenopacket, Procedure, PhenotypicFeature
from chord_metadata_service.experiments.models import Experiment, ExperimentResult, Instrument
from chord_metadata_service.phenopackets.tests.constants import (
    VALID_PROCEDURE_1,
    valid_biosample_1,
    valid_biosample_2,
    VALID_META_DATA_1,
)
from chord_metadata_service.experiments.tests.constants import (
    valid_experiment, valid_experiment_result, valid_instrument
)

from chord_metadata_service.chord.tests.es_mocks import SEARCH_SUCCESS
from .constants import (
    VALID_PROJECT_1,
    valid_dataset_1,
    valid_table_1,
    valid_phenotypic_feature,
    TEST_SEARCH_QUERY_1,
    TEST_SEARCH_QUERY_2,
    TEST_SEARCH_QUERY_3,
    TEST_SEARCH_QUERY_4,
    TEST_SEARCH_QUERY_5,
    TEST_SEARCH_QUERY_6,
    TEST_SEARCH_QUERY_7,
    TEST_SEARCH_QUERY_8,
    TEST_SEARCH_QUERY_9,
    TEST_SEARCH_QUERY_10,
    TEST_FHIR_SEARCH_QUERY,
)
from ..models import Project, Dataset, TableOwnership, Table
from ..data_types import (
    DATA_TYPE_EXPERIMENT,
    DATA_TYPE_PHENOPACKET
)

POST_GET = ("POST", "GET")


class SearchTest(APITestCase):
    def setUp(self) -> None:
        self.project = Project.objects.create(**VALID_PROJECT_1)
        self.dataset = Dataset.objects.create(**valid_dataset_1(self.project))

        # Set up a dummy phenopacket

        self.individual, _ = Individual.objects.get_or_create(
            id='patient:1', sex='FEMALE', age={"age": "P25Y3M2D"})

        self.procedure = Procedure.objects.create(**VALID_PROCEDURE_1)

        self.biosample_1 = Biosample.objects.create(**valid_biosample_1(self.individual, self.procedure))
        self.biosample_2 = Biosample.objects.create(**valid_biosample_2(None, self.procedure))

        self.meta_data = MetaData.objects.create(**VALID_META_DATA_1)

        self.phenopacket = Phenopacket.objects.create(
            id="phenopacket_id:1",
            subject=self.individual,
            meta_data=self.meta_data,
            dataset=self.dataset
        )

        self.phenopacket.biosamples.set([self.biosample_1, self.biosample_2])

        self.phenotypic_feature = PhenotypicFeature.objects.create(
            **valid_phenotypic_feature(phenopacket=self.phenopacket)
        )

        # add Experiments metadata and link to self.biosample_1
        self.instrument = Instrument.objects.create(**valid_instrument())
        self.experiment_result = ExperimentResult.objects.create(**valid_experiment_result())
        self.experiment = Experiment.objects.create(**valid_experiment(
            biosample=self.biosample_1, instrument=self.instrument, dataset=self.dataset))
        self.experiment.experiment_results.set([self.experiment_result])

    def _search_call(self, endpoint, args=None, data=None, method="GET"):
        args = args or []

        if method == "POST":
            data = json.dumps(data)
        else:
            data = data if data is None or "query" not in data else {
                **data,
                "query": json.dumps(data["query"]),
            }

        return (self.client.post if method == "POST" else self.client.get)(
            reverse(endpoint, args=args),
            data=data,
            **({"content_type": "application/json"} if method == "POST" else {}))

    def test_common_search_1(self):
        # No body
        for method in POST_GET:
            r = self._search_call("search", method=method)
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_common_search_2(self):
        # No data type
        for method in POST_GET:
            r = self._search_call("search", data={"query": TEST_SEARCH_QUERY_1}, method=method)
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_common_search_3(self):
        # No query
        for method in POST_GET:
            r = self._search_call("search", data={"data_type": DATA_TYPE_PHENOPACKET}, method=method)
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_common_search_4(self):
        # Bad data type
        for method in POST_GET:
            r = self._search_call("search", data={
                "data_type": "bad_data_type",
                "query": TEST_SEARCH_QUERY_1,
            }, method=method)
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_common_search_5(self):
        # Bad syntax for query
        for method in POST_GET:
            r = self._search_call("search", data={
                "data_type": DATA_TYPE_PHENOPACKET,
                "query": ["hello", "world"]
            }, method=method)
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_with_result(self):
        # Valid search with result
        for method in POST_GET:
            r = self._search_call("search", data={
                "data_type": DATA_TYPE_PHENOPACKET,
                "query": TEST_SEARCH_QUERY_1
            }, method=method)
            self.assertEqual(r.status_code, status.HTTP_200_OK)

            c = r.json()

            self.assertEqual(len(c["results"]), 1)
            self.assertDictEqual(c["results"][0], {
                "id": str(self.table.identifier),
                "data_type": DATA_TYPE_PHENOPACKET
            })

    def test_search_without_result(self):
        # Valid search without result
        for method in POST_GET:
            r = self._search_call("search", data={
                "data_type": DATA_TYPE_PHENOPACKET,
                "query": TEST_SEARCH_QUERY_2
            }, method=method)
            self.assertEqual(r.status_code, status.HTTP_200_OK)
            c = r.json()
            self.assertEqual(len(c["results"]), 0)

    def test_private_search(self):
        # Valid search with result
        for method in POST_GET:
            r = self._search_call("private-search", data={
                "data_type": DATA_TYPE_PHENOPACKET,
                "query": TEST_SEARCH_QUERY_1
            }, method=method)
            self.assertEqual(r.status_code, status.HTTP_200_OK)
            c = r.json()

            self.assertIn(str(self.dataset.identifier), c["results"])
            self.assertEqual(c["results"][str(self.table.identifier)]["data_type"], DATA_TYPE_PHENOPACKET)
            self.assertEqual(self.phenopacket.id, c["results"][str(self.table.identifier)]["matches"][0]["id"])

        # TODO: Check schema?

    
    def test_private_search_10_experiment(self):
        # Valid search with result

        d = {
            "data_type": DATA_TYPE_EXPERIMENT,
            "query": TEST_SEARCH_QUERY_7
        }

        for method in POST_GET:
            r = self._search_call("private-search", data=d, method=method)
            self.assertEqual(r.status_code, status.HTTP_200_OK)
            c = r.json()
            self.assertIn(str(self.dataset.identifier), c["results"])
            self.assertEqual(c["results"][str(self.t_exp.identifier)]["data_type"], DATA_TYPE_EXPERIMENT)
            self.assertEqual(self.experiment.id, c["results"][str(self.t_exp.identifier)]["matches"][0]["id"])
            self.assertEqual(len(c["results"][str(self.t_exp.identifier)]["matches"]), 1)
            self.assertEqual(c["results"][str(self.t_exp.identifier)]["matches"][0]["id"], "experiment:1")
            self.assertEqual(c["results"][str(self.t_exp.identifier)]["matches"][0]["study_type"],
                             "Whole genome Sequencing")
            self.assertEqual(c["results"][str(self.t_exp.identifier)]["matches"][0]["molecule"], "total RNA")
            self.assertEqual(len(c["results"][str(self.t_exp.identifier)]["matches"][0]["experiment_results"]), 1)
            self.assertEqual(
                c["results"][str(self.t_exp.identifier)]["matches"][0]["experiment_results"][0]["file_format"], "VCF"
            )
            self.assertEqual(c["results"][str(self.t_exp.identifier)]["matches"][0]["instrument"]["identifier"],
                             "instrument:01")
            self.assertEqual(c["results"][str(self.t_exp.identifier)]["matches"][0]["instrument"]["platform"],
                             "Illumina")
            self.assertEqual(c["results"][str(self.t_exp.identifier)]["matches"][0]["instrument"]["model"],
                             "Illumina HiSeq 4000")
            self.assertEqual(c["results"][str(self.t_exp.identifier)]["matches"][0]["instrument"]["extra_properties"],
                             {"date": "2021-06-21"})

    def test_private_search_11_experiment(self):
        # Valid search with result, case-insensitive search for experiment_type

        d = {
            "data_type": DATA_TYPE_EXPERIMENT,
            "query": TEST_SEARCH_QUERY_8
        }

        for method in POST_GET:
            r = self._search_call("private-search", data=d, method=method)
            self.assertEqual(r.status_code, status.HTTP_200_OK)
            c = r.json()
            self.assertIn(str(self.dataset.identifier), c["results"])
            self.assertEqual(c["results"][str(self.t_exp.identifier)]["data_type"], DATA_TYPE_EXPERIMENT)
            self.assertEqual(c["results"][str(self.t_exp.identifier)]["matches"][0]["experiment_type"],
                             "DNA Methylation")

    
    def test_private_search_bento_search_results(self):
        # Valid query to search for biosample id in list
        # Output as a bento search is valid

        d = {
            "query": TEST_SEARCH_QUERY_10,
            "output": "bento_search_result",
            "data_type": "phenopacket",
        }

        for method in POST_GET:
            r = self._search_call("private-search", data=d, method=method)
            self.assertEqual(r.status_code, status.HTTP_200_OK)
            c = r.json()
            table_id = list(c["results"].keys())[0]
            matches = c["results"][table_id]["matches"]
            self.assertEqual(len(matches), 1)   # 1 matching phenopacket

    def test_private_search_values_list(self):
        # Valid query to search for biosample id in list
        # Output as a list of values

        d = {
            "query": TEST_SEARCH_QUERY_10,
            "output": "values_list",
            "field": '["biosamples", "[item]", "id"]',
            "data_type": "phenopacket",
        }

        for method in POST_GET:
            r = self._search_call("private-search", data=d, method=method)
            self.assertEqual(r.status_code, status.HTTP_200_OK)
            c = r.json()
            table_id = list(c["results"].keys())[0]
            matches = c["results"][table_id]["matches"]
            self.assertEqual(len(matches), 2)   # 2 biosamples in list

    @patch('chord_metadata_service.chord.views_search.es')
    def test_fhir_search(self, mocked_es):
        mocked_es.search.return_value = SEARCH_SUCCESS
        # Valid search with result
        for method in POST_GET:
            r = self._search_call("fhir-search", data={
                "query": TEST_FHIR_SEARCH_QUERY
            }, method=method)

            self.assertEqual(r.status_code, status.HTTP_200_OK)
            c = r.json()

            self.assertEqual(len(c["results"]), 1)
            self.assertDictEqual(c["results"][0], {
                "id": str(self.table.identifier),
                "data_type": DATA_TYPE_PHENOPACKET
            })

    @patch('chord_metadata_service.chord.views_search.es')
    def test_private_fhir_search(self, mocked_es):
        mocked_es.search.return_value = SEARCH_SUCCESS
        # Valid search with result
        for method in POST_GET:
            r = self._search_call("fhir-private-search", data={
                "query": TEST_FHIR_SEARCH_QUERY
            }, method=method)

            self.assertEqual(r.status_code, status.HTTP_200_OK)
            c = r.json()

            self.assertIn(str(self.dataset.identifier), c["results"])
            self.assertEqual(c["results"][str(self.dataset.identifier)]["data_type"], DATA_TYPE_PHENOPACKET)
            self.assertEqual(self.phenopacket.id, c["results"][str(self.table.identifier)]["matches"][0]["id"])
