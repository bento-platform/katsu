import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from chord_metadata_service.chord.tests.example_ingest import EXAMPLE_INGEST_EXPERIMENT, \
    EXAMPLE_INGEST_INVALID_EXPERIMENT, EXAMPLE_INGEST_INVALID_PHENOPACKET, EXAMPLE_INGEST_PHENOPACKET
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
            reverse("ingest-into-dataset", args=(self.dataset["identifier"], "phenopackets_json_invalid")),
            content_type="application/json",
        )
        c = r.json()
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(c["success"], False)
        self.assertEqual(len(c["errors"]), 1)

        # No ingestion body
        r = self.client.post(
            reverse("ingest-into-dataset", args=(self.dataset["identifier"], "phenopackets_json")),
            content_type="application/json",
        )
        c = r.json()
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(c["success"], False)
        self.assertEqual(len(c["errors"]), 1)

        # Bad ingestion body JSON
        r = self.client.post(
            reverse("ingest-into-dataset", args=(self.dataset["identifier"], "phenopackets_json")),
            content_type="application/json",
            data="\{\}\}",  # noqa: W605
        )
        c = r.json()
        self.assertEqual(r.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(c["success"], False)
        self.assertEqual(len(c["errors"]), 1)  # 1 required property

        # Invalid phenopacket JSON validation
        r = self.client.post(
            reverse("ingest-into-dataset", args=(self.dataset["identifier"], "phenopackets_json")),
            content_type="application/json",
            data=json.dumps(EXAMPLE_INGEST_INVALID_PHENOPACKET),
        )
        c = r.json()
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(c["success"], False)
        self.assertEqual(len(c["errors"]), 2)

        # Success
        r = self.client.post(
            reverse("ingest-into-dataset", args=(self.dataset["identifier"], "phenopackets_json")),
            content_type="application/json",
            data=json.dumps(EXAMPLE_INGEST_PHENOPACKET),
        )
        c = r.json()
        self.assertEqual(c["success"], True)
        self.assertEqual(len(c["errors"]), 0)
        self.assertEqual(len(c["warnings"]), 0)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_experiments_ingest_failures(self):
        # Invalid workflow ID
        r = self.client.post(
            reverse("ingest-into-dataset", args=(self.dataset["identifier"], "experiments_json_invalid")),
            content_type="application/json",
        )
        c = r.json()
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(c["success"], False)
        self.assertEqual(len(c["errors"]), 1)

        # No ingestion body
        r = self.client.post(
            reverse("ingest-into-dataset", args=(self.dataset["identifier"], "experiments_json")),
            content_type="application/json",
        )
        c = r.json()
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(c["success"], False)
        self.assertEqual(len(c["errors"]), 2)  # 2 required properties

        # Bad ingestion body JSON
        r = self.client.post(
            reverse("ingest-into-dataset", args=(self.dataset["identifier"], "experiments_json")),
            content_type="application/json",
            data="\{\}\}",  # noqa: W605
        )
        c = r.json()
        self.assertEqual(r.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(c["success"], False)
        self.assertEqual(len(c["errors"]), 1)

        # Invalid experiments JSON validation
        r = self.client.post(
            reverse("ingest-into-dataset", args=(self.dataset["identifier"], "experiments_json")),
            content_type="application/json",
            data=json.dumps(EXAMPLE_INGEST_INVALID_EXPERIMENT),
        )
        c = r.json()
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(c["success"], False)
        self.assertEqual(len(c["errors"]), 4)

        # Two of the errors concern experiment schema changes
        warnings = c["warnings"]
        self.assertEqual(len(warnings), 2)
        warned_properties = [schema_warning["property_name"] for schema_warning in warnings]
        self.assertTrue("library_selection" in warned_properties)
        self.assertTrue("library_strategy" in warned_properties)

        # Biosample not present
        r = self.client.post(
            reverse("ingest-into-dataset", args=(self.dataset["identifier"], "experiments_json")),
            content_type="application/json",
            data=json.dumps(EXAMPLE_INGEST_EXPERIMENT),
        )
        c = r.json()
        self.assertEqual(c["success"], False)
        self.assertEqual(len(c["errors"]), 1)
        self.assertEqual(r.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_experiment_ingest_success(self):
        # Create the required phenopacket with a biosample first
        r = self.client.post(
            reverse("ingest-into-dataset", args=(self.dataset["identifier"], "phenopackets_json")),
            content_type="application/json",
            data=json.dumps(EXAMPLE_INGEST_PHENOPACKET),
        )

        # Ingest experiment
        r = self.client.post(
            reverse("ingest-into-dataset", args=(self.dataset["identifier"], "experiments_json")),
            content_type="application/json",
            data=json.dumps(EXAMPLE_INGEST_EXPERIMENT),
        )
        c = r.json()
        self.assertEqual(c["success"], True)
        self.assertEqual(len(c["errors"]), 0)
        self.assertEqual(len(c["warnings"]), 0)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
