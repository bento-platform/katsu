import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from chord_metadata_service.restapi.tests.utils import load_local_json
from .constants import VALID_PROJECT_1, valid_dataset_1
from ..workflows.metadata import workflow_set, WORKFLOW_PHENOPACKETS_JSON


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

        # Non-existent workflow
        r = self.client.get(reverse("workflow-detail", args=("invalid_workflow",)), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

        # Valid workflow
        r = self.client.get(reverse("workflow-detail", args=("phenopackets_json",)), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertDictEqual(r.json(), workflow_set.get_workflow(WORKFLOW_PHENOPACKETS_JSON).model_dump(mode="json"))

        # Non-existent workflow file
        r = self.client.get(reverse("workflow-file", args=("invalid_workflow",)), content_type="text/plain")
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

        # Valid workflow file
        r = self.client.get(reverse("workflow-file", args=("phenopackets_json",)), content_type="text/plain")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        # TODO: Check file contents


class IngestTest(APITestCase):
    def setUp(self) -> None:
        r = self.client.post(reverse("project-list"), data=json.dumps(VALID_PROJECT_1), content_type="application/json")
        self.project = r.json()

        r = self.client.post('/api/datasets', data=json.dumps(valid_dataset_1(self.project["identifier"])),
                             content_type="application/json")
        self.dataset = r.json()

    def test_phenopackets_ingest(self):
        # Invalid workflow ID
        r = self.client.post(
            reverse("ingest-into-dataset", args=(self.dataset["identifier"], "phenopackets_json_invalid")),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        # No ingestion body
        r = self.client.post(
            reverse("ingest-into-dataset", args=(self.dataset["identifier"], "phenopackets_json")),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        # Bad ingestion body JSON
        r = self.client.post(
            reverse("ingest-into-dataset", args=(self.dataset["identifier"], "phenopackets_json")),
            content_type="application/json",
            data="\{\}\}",  # noqa: W605
        )
        self.assertEqual(r.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Invalid phenopacket JSON validation
        invalid_phenopacket = load_local_json("example_invalid_phenopacket.json")
        r = self.client.post(
            reverse("ingest-into-dataset", args=(self.dataset["identifier"], "phenopackets_json")),
            content_type="application/json",
            data=json.dumps(invalid_phenopacket),
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        # Success
        valid_phenopacket = load_local_json("example_phenopacket_v2.json")
        r = self.client.post(
            reverse("ingest-into-dataset", args=(self.dataset["identifier"], "phenopackets_json")),
            content_type="application/json",
            data=json.dumps(valid_phenopacket),
        )
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
