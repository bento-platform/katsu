import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .constants import VALID_PROJECT_1, valid_dataset_1
from ..workflows.metadata import METADATA_WORKFLOWS


def generate_phenopackets_ingest(dataset_id):
    return {
        "dataset_id": dataset_id,
        "workflow_id": "phenopackets_json",
        "workflow_metadata": METADATA_WORKFLOWS["ingestion"]["phenopackets_json"],
        "workflow_outputs": {
            "json_document": ""  # TODO
        },
        "workflow_params": {
            "json_document": ""  # TODO
        }
    }


class WorkflowTest(APITestCase):
    def test_workflows(self):
        r = self.client.get(reverse("workflows"), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertDictEqual(r.json(), METADATA_WORKFLOWS)

        # Non-existent workflow
        r = self.client.get(reverse("workflow-detail", args=("invalid_workflow",)), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

        # Valid workflow
        r = self.client.get(reverse("workflow-detail", args=("phenopackets_json",)), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertDictEqual(r.json(), METADATA_WORKFLOWS["ingestion"]["phenopackets_json"])

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
            reverse("ingest-into-dataset", args=(self.dataset["identifier"],"phenopackets_json_invalid")),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        # No ingestion body
        r = self.client.post(
            reverse("ingest-into-dataset", args=(self.dataset["identifier"], "phenopackets_json")),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
