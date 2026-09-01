import uuid
from unittest.mock import patch

from django.core.exceptions import ValidationError as DjangoValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from chord_metadata_service.chord.ingest import WORKFLOW_INGEST_FUNCTION_MAP
from chord_metadata_service.chord.workflows.metadata import (
    workflow_set,
    WORKFLOW_PHENOPACKETS_JSON,
    WORKFLOW_EXPERIMENTS_JSON,
)
from chord_metadata_service.logger import logger
from chord_metadata_service.restapi.tests.utils import load_local_json

from .constants import valid_dataset
from .example_ingest import (
    EXAMPLE_INGEST_PHENOPACKET,
    EXAMPLE_INGEST_EXPERIMENT,
    EXAMPLE_INGEST_EXPERIMENT_RESULT,
)
from .helpers import AuthzAPITestCaseWithProjectJSON


def generate_phenopackets_ingest(dataset_id):
    return {
        "dataset_id": dataset_id,
        "workflow_id": "phenopackets_json",
        "workflow_metadata": workflow_set.get_workflow(WORKFLOW_PHENOPACKETS_JSON),
        "workflow_params": {
            "json_document": ""  # TODO
        }
    }


class WorkflowTest(APITestCase):
    def test_workflows(self):
        r = self.client.get(reverse("workflows"), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertDictEqual(r.json(), workflow_set.workflow_dicts_by_type_and_id())

        # Valid workflow
        r = self.client.get(reverse("workflow-detail", args=("phenopackets_json",)), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertDictEqual(r.json(), workflow_set.get_workflow(WORKFLOW_PHENOPACKETS_JSON).model_dump(mode="json"))

        # Valid workflow file
        r = self.client.get(reverse("workflow-file", args=("phenopackets_json",)), content_type="text/plain")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        # TODO: Check file contents

    def test_workflow_404(self):
        # Non-existent workflow
        r = self.client.get(reverse("workflow-detail", args=("invalid_workflow",)), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

        # Non-existent workflow file
        r = self.client.get(reverse("workflow-file", args=("invalid_workflow",)), content_type="text/plain")
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)


class APITestCaseWithDataset(AuthzAPITestCaseWithProjectJSON):
    def setUp(self) -> None:
        super().setUp()
        r = self.one_authz_post("/api/datasets", json=valid_dataset(self.project["identifier"]))
        self.dataset = r.json()
        self.dataset_id = self.dataset["identifier"]


class IngestTest(APITestCaseWithDataset):
    def test_phenopackets_ingest_400s(self):
        # Bad dataset ID
        r = self.one_authz_post(
            reverse("ingest-into-dataset", args=(str(uuid.uuid4()), WORKFLOW_PHENOPACKETS_JSON)),
            json=load_local_json("example_phenopacket_v2.json"),
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid workflow ID
        r = self.one_authz_post(
            reverse("ingest-into-dataset", args=(self.dataset_id, "phenopackets_json_invalid")),
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        # No ingestion body
        r = self.one_authz_post(
            reverse("ingest-into-dataset", args=(self.dataset_id, WORKFLOW_PHENOPACKETS_JSON)),
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        # Bad ingestion body JSON - JSON parse error 400
        r = self.one_authz_post(
            reverse("ingest-into-dataset", args=(self.dataset_id, WORKFLOW_PHENOPACKETS_JSON)),
            content_type="application/json",
            data="{}}",  # noqa: W605
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid phenopacket JSON validation
        invalid_phenopacket = load_local_json("example_invalid_phenopacket.json")
        r = self.one_authz_post(
            reverse("ingest-into-dataset", args=(self.dataset_id, WORKFLOW_PHENOPACKETS_JSON)),
            json=invalid_phenopacket,
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_phenopackets_ingest_valid(self):
        # Success
        r = self.one_authz_post(
            reverse("ingest-into-dataset", args=(self.dataset_id, WORKFLOW_PHENOPACKETS_JSON)),
            json=load_local_json("example_phenopacket_v2.json"),
        )
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)

    def test_phenopackets_ingest_forbidden(self):
        # Forbidden
        r = self.one_no_authz_post(
            reverse("ingest-into-dataset", args=(self.dataset_id, WORKFLOW_PHENOPACKETS_JSON)),
            json=load_local_json("example_phenopacket_v2.json"),
        )
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_ingest_validation_error_returns_400(self):
        def _raise(*_):
            raise DjangoValidationError("invalid")

        with patch.dict("chord_metadata_service.chord.ingest.views.WORKFLOW_INGEST_FUNCTION_MAP",
                        {WORKFLOW_PHENOPACKETS_JSON: _raise}):
            r = self.one_authz_post(
                reverse("ingest-into-dataset", args=(self.dataset_id, WORKFLOW_PHENOPACKETS_JSON)),
                json={},
            )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ingest_unexpected_exception_returns_500(self):
        def _raise(*_):
            raise RuntimeError("unexpected")

        with patch.dict("chord_metadata_service.chord.ingest.views.WORKFLOW_INGEST_FUNCTION_MAP",
                        {WORKFLOW_PHENOPACKETS_JSON: _raise}):
            r = self.one_authz_post(
                reverse("ingest-into-dataset", args=(self.dataset_id, WORKFLOW_PHENOPACKETS_JSON)),
                json={},
            )
        self.assertEqual(r.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class IngestDerivedExperimentResultsTest(APITestCaseWithDataset):
    def setUp(self) -> None:
        super().setUp()

        # ingest list of experiments
        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](EXAMPLE_INGEST_PHENOPACKET, self.dataset_id, logger)
        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_EXPERIMENTS_JSON](EXAMPLE_INGEST_EXPERIMENT, self.dataset_id, logger)

    def test_ingest_derived_experiment_results(self):
        # ingest list of experiment results
        r = self.one_authz_post(
            reverse("ingest-derived-experiment-results", args=(self.dataset_id,)),
            json=EXAMPLE_INGEST_EXPERIMENT_RESULT,
        )

        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)

    def test_ingest_derived_experiment_results_forbidden(self):
        # forbidden
        r = self.one_no_authz_post(
            reverse("ingest-derived-experiment-results", args=(self.dataset_id,)),
            json=EXAMPLE_INGEST_EXPERIMENT_RESULT,
        )
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_ingest_derived_experiment_results_dataset_dne(self):
        r = self.one_authz_post(
            reverse("ingest-derived-experiment-results", args=(str(uuid.uuid4()),)),
            json=EXAMPLE_INGEST_EXPERIMENT_RESULT,
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
