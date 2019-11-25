import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .constants import *
from ..models import *


class CreateProjectTest(APITestCase):
    def setUp(self) -> None:
        self.valid_payloads = [
            VALID_PROJECT_1,
            {
                "name": "Project 2",
                "description": "",
                "data_use": VALID_DATA_USE_1
            }
        ]

        self.invalid_payloads = [
            {
                "name": "Project 1",
                "description": "",
                "data_use": {}
            },
            {
                "name": "aa",
                "description": "",
                "data_use": VALID_DATA_USE_1
            }
        ]

    def test_create_project(self):
        for i, p in enumerate(self.valid_payloads, 1):
            r = self.client.post(reverse("project-list"), data=json.dumps(p), content_type="application/json")
            self.assertEqual(r.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Project.objects.count(), i)
            self.assertEqual(Project.objects.get(name=p["name"]).description, p["description"])
            self.assertDictEqual(Project.objects.get(name=p["name"]).data_use, p["data_use"])

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
            valid_dataset_1(self.project["project_id"])
        ]

        self.invalid_payloads = [
            {
                "name": "aa",
                "description": "Test Dataset",
                "project": self.project["project_id"]
            },
            {
                "name": "Dataset 1",
                "description": "Test Dataset",
                "project": None
            }
        ]

    def test_create_dataset(self):
        for i, d in enumerate(self.valid_payloads, 1):
            r = self.client.post(reverse("dataset-list"), data=json.dumps(d), content_type="application/json")
            self.assertEqual(r.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Dataset.objects.count(), i)
            self.assertEqual(Dataset.objects.get(name=d["name"]).description, d["description"])

        for d in self.invalid_payloads:
            r = self.client.post(reverse("dataset-list"), data=json.dumps(d), content_type="application/json")
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(Dataset.objects.count(), len(self.valid_payloads))

# TODO: Update Dataset
# TODO: Delete Dataset
# TODO: Create TableOwnership
# TODO: Update TableOwnership
# TODO: Delete TableOwnership
