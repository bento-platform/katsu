import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .constants import *
from ..views_search import PHENOPACKET_DATA_TYPE_ID, PHENOPACKET_SCHEMA, PHENOPACKET_METADATA_SCHEMA


class DataTypeTest(APITestCase):
    def test_data_type_list(self):
        r = self.client.get(reverse("data-type-list"))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertEqual(len(c), 1)
        self.assertEqual(c[0]["id"], PHENOPACKET_DATA_TYPE_ID)

    def test_data_type_detail(self):
        r = self.client.get(reverse("data-type-detail"))  # Only mounted with phenopacket right now
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertDictEqual(c, {
            "id": PHENOPACKET_DATA_TYPE_ID,
            "schema": PHENOPACKET_SCHEMA,
            "metadata_schema": PHENOPACKET_METADATA_SCHEMA
        })

    def test_data_type_schema(self):
        r = self.client.get(reverse("data-type-schema"))  # Only mounted with phenopacket right now
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertDictEqual(c, PHENOPACKET_SCHEMA)

    def test_data_type_metadata_schema(self):
        r = self.client.get(reverse("data-type-metadata-schema"))  # Only mounted with phenopacket right now
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertDictEqual(c, PHENOPACKET_METADATA_SCHEMA)


class TableTest(APITestCase):
    @staticmethod
    def dataset_rep(dataset, created, updated):
        return {
            "id": dataset["dataset_id"],
            "name": dataset["name"],
            "metadata": {
                "description": dataset["description"],
                "project_id": dataset["project"],
                "created": created,
                "updated": updated
            },
            "schema": PHENOPACKET_SCHEMA
        }

    def setUp(self) -> None:
        # Add example data

        r = self.client.post(reverse("project-list"), data=json.dumps(VALID_PROJECT_1), content_type="application/json")
        self.project = r.json()

        r = self.client.post(reverse("dataset-list"), data=json.dumps(valid_dataset_1(self.project["project_id"])),
                             content_type="application/json")
        self.dataset = r.json()

    def test_table_list(self):
        # No data type specified
        r = self.client.get(reverse("table-list"))
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

        r = self.client.get(reverse("table-list"), {"data-type": PHENOPACKET_DATA_TYPE_ID})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertEqual(len(c), 1)
        self.assertEqual(c[0], self.dataset_rep(self.dataset, c[0]["metadata"]["created"], c[0]["metadata"]["updated"]))
