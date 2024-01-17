import json
from django.db.utils import IntegrityError

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .constants import (
    VALID_PROJECT_1,
    VALID_DATA_USE_1,
    valid_dataset_1,
    dats_dataset,
    VALID_DATS_CREATORS,
    INVALID_DATS_CREATORS,
    valid_project_json_schema,
)
from ..models import Project, Dataset, ProjectJsonSchema


class CreateProjectTest(APITestCase):
    def setUp(self) -> None:
        self.valid_payloads = [
            VALID_PROJECT_1,
            {
                "title": "Project 2",
                "description": "",
                "data_use": VALID_DATA_USE_1
            }
        ]

        self.invalid_payloads = [
            {
                "title": "Project 1",
                "description": "",
                "data_use": {}
            },
            {
                "title": "aa",
                "description": "",
                "data_use": VALID_DATA_USE_1
            }
        ]

    def test_create_project(self):
        for i, p in enumerate(self.valid_payloads, 1):
            r = self.client.post(reverse("project-list"), data=json.dumps(p), content_type="application/json")
            self.assertEqual(r.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Project.objects.count(), i)
            self.assertEqual(Project.objects.get(title=p["title"]).description, p["description"])

        for p in self.invalid_payloads:
            r = self.client.post(reverse("project-list"), data=json.dumps(p), content_type="application/json")
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(Project.objects.count(), len(self.valid_payloads))


# TODO: Update Project
# TODO: Delete Project

class CreateDatasetTest(APITestCase):
    def setUp(self) -> None:
        r = self.client.post(reverse("project-list"), data=json.dumps(VALID_PROJECT_1), content_type="application/json")
        self.project = r.json()

        self.valid_payloads = [
            valid_dataset_1(self.project["identifier"]),
            {
                **valid_dataset_1(self.project["identifier"]),
                "title": "Dataset 2",
                "dats_file": {},  # Valid dats_file JSON object
            },
            {
                **valid_dataset_1(self.project["identifier"]),
                "title": "Dataset 3",
                "dats_file": "{}",  # Valid dats_file JSON string
            }
        ]

        self.dats_valid_payload = dats_dataset(self.project["identifier"], VALID_DATS_CREATORS)
        self.dats_invalid_payload = dats_dataset(self.project["identifier"], INVALID_DATS_CREATORS)

        self.invalid_payloads = [
            {
                "title": "aa",
                "description": "Test Dataset",
                "project": self.project["identifier"]
            },
            {
                "title": "Dataset 1",
                "description": "Test Dataset",
                "project": None
            },
            {
                **valid_dataset_1(self.project["identifier"]),
                "title": "Dataset 4",
                "dats_file": "INVALID_JSON_STRING",
            },
        ]

    def test_create_dataset(self):
        for i, d in enumerate(self.valid_payloads, 1):
            r = self.client.post('/api/datasets', data=json.dumps(d), content_type="application/json")
            self.assertEqual(r.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Dataset.objects.count(), i)
            self.assertEqual(Dataset.objects.get(title=d["title"]).description, d["description"])
            self.assertDictEqual(Dataset.objects.get(title=d["title"]).data_use, d["data_use"])

        for d in self.invalid_payloads:
            r = self.client.post('/api/datasets', data=json.dumps(d), content_type="application/json")
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(Dataset.objects.count(), len(self.valid_payloads))

    def test_dats(self):
        payload = {**self.dats_valid_payload, 'dats_file': {}}
        r = self.client.post('/api/datasets', data=json.dumps(payload),
                             content_type="application/json")
        r_invalid = self.client.post('/api/datasets', data=json.dumps(self.dats_invalid_payload),
                                     content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r_invalid.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Dataset.objects.count(), 1)

        dataset_id = Dataset.objects.first().identifier

        url = f'/api/datasets/{dataset_id}/dats'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, payload['dats_file'])

    def test_resources(self):
        resource = {
            "id": "NCBITaxon:2023-09-14",
            "name": "NCBI Taxonomy OBO Edition",
            "version": "2023-09-14",
            "namespace_prefix": "NCBITaxon",
            "url": "http://purl.obolibrary.org/obo/ncbitaxon/2023-09-14/ncbitaxon.owl",
            "iri_prefix": "http://purl.obolibrary.org/obo/NCBITaxon_",
        }

        r = self.client.post("/api/resources", data=json.dumps(resource), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        r = self.client.post(
            "/api/datasets",
            data=json.dumps({
                **valid_dataset_1(self.project["identifier"]),
                "additional_resources": [resource["id"]],
            }),
            content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        dataset_id = Dataset.objects.first().identifier
        r = self.client.get(f"/api/datasets/{dataset_id}/resources")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.data), 1)
        self.assertEqual(r.data[0]["id"], resource["id"])


# TODO: Update Dataset
# TODO: Delete Dataset


class CreateProjectJsonSchema(APITestCase):

    def setUp(self) -> None:
        # Create project
        r = self.client.post(reverse("project-list"), data=json.dumps(VALID_PROJECT_1), content_type="application/json")
        self.project = r.json()

        # Valid payload and project_id
        self.project_json_schema_valid_payload = valid_project_json_schema(project_id=self.project["identifier"])
        # Invalid project_id
        self.project_json_schema_invalid_payload = valid_project_json_schema(project_id="an-id-that-does-not-exist")

    def test_create_project_json_schema(self):
        r = self.client.post('/api/project_json_schemas',
                             data=json.dumps(self.project_json_schema_valid_payload),
                             content_type="application/json")
        r_invalid = self.client.post('/api/project_json_schemas',
                                     data=json.dumps(self.project_json_schema_invalid_payload),
                                     content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r_invalid.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ProjectJsonSchema.objects.count(), 1)

    def test_create_constraint(self):
        r = self.client.post('/api/project_json_schemas',
                             data=json.dumps(self.project_json_schema_valid_payload),
                             content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        with self.assertRaises(IntegrityError):
            r_duplicate = self.client.post('/api/project_json_schemas',
                                           data=json.dumps(self.project_json_schema_valid_payload),
                                           content_type="application/json")
            self.assertEqual(r_duplicate, status.HTTP_500_INTERNAL_SERVER_ERROR)
