import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from chord_metadata_service.phenopackets.tests.constants import *
from chord_metadata_service.phenopackets.models import *

from .constants import *
from ..models import *
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
            "id": dataset["identifier"],
            "name": dataset["title"],
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

        r = self.client.post(reverse("dataset-list"), data=json.dumps(valid_dataset_1(self.project["identifier"])),
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


class SearchTest(APITestCase):
    def setUp(self) -> None:
        self.project = Project.objects.create(**VALID_PROJECT_1)
        self.dataset = Dataset.objects.create(**valid_dataset_1(self.project))

        # Set up a dummy phenopacket

        self.individual, _ = Individual.objects.get_or_create(
            id='patient:1', sex='FEMALE', age='P25Y3M2D')

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

    def test_common_search(self):
        # No body
        r = self.client.post(reverse("search"))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        # No data type
        r = self.client.post(reverse("search"), data=json.dumps({"query": TEST_SEARCH_QUERY_1}),
                             content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        # No query
        r = self.client.post(reverse("search"), data=json.dumps({"data_type": PHENOPACKET_DATA_TYPE_ID}),
                             content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        # Bad data type
        r = self.client.post(reverse("search"), data=json.dumps({
            "data_type": "bad_data_type",
            "query": TEST_SEARCH_QUERY_1
        }), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        # Bad syntax for query
        r = self.client.post(reverse("search"), data=json.dumps({
            "data_type": PHENOPACKET_DATA_TYPE_ID,
            "query": ["hello", "world"]
        }), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search(self):
        # Valid search with result
        r = self.client.post(reverse("search"), data=json.dumps({
            "data_type": PHENOPACKET_DATA_TYPE_ID,
            "query": TEST_SEARCH_QUERY_1
        }), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertEqual(len(c["results"]), 1)
        self.assertDictEqual(c["results"][0], {
            "id": str(self.dataset.identifier),
            "data_type": PHENOPACKET_DATA_TYPE_ID
        })

        # Valid search without result
        r = self.client.post(reverse("search"), data=json.dumps({
            "data_type": PHENOPACKET_DATA_TYPE_ID,
            "query": TEST_SEARCH_QUERY_2
        }), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertEqual(len(c["results"]), 0)

    def test_private_search(self):
        # Valid search with result
        r = self.client.post(reverse("private-search"), data=json.dumps({
            "data_type": PHENOPACKET_DATA_TYPE_ID,
            "query": TEST_SEARCH_QUERY_1
        }), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertIn(str(self.dataset.identifier), c["results"])
        self.assertEqual(c["results"][str(self.dataset.identifier)]["data_type"], PHENOPACKET_DATA_TYPE_ID)
        self.assertEqual(self.phenopacket.id, c["results"][str(self.dataset.identifier)]["matches"][0]["id"])
        # TODO: Check schema?

    def test_private_table_search(self):
        # No body
        r = self.client.post(reverse("table-search", args=[str(self.dataset.identifier)]))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        # No query
        r = self.client.post(reverse("table-search", args=[str(self.dataset.identifier)]), data=json.dumps({}),
                             content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        # Bad syntax for query
        r = self.client.post(reverse("table-search", args=[str(self.dataset.identifier)]), data=json.dumps({
            "query": ["hello", "world"]
        }), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        # Valid query with one result
        r = self.client.post(reverse("table-search", args=[str(self.dataset.identifier)]), data=json.dumps({
            "query": TEST_SEARCH_QUERY_1
        }), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertEqual(len(c["results"]), 1)
        self.assertEqual(self.phenopacket.id, c["results"][0]["id"])
