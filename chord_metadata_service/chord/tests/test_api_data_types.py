from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..data_types import (
    DATA_TYPE_EXPERIMENT,
    DATA_TYPE_EXPERIMENT_RESULT,
    DATA_TYPE_PHENOPACKET,
    DATA_TYPE_READSET,
    DATA_TYPES
)
from ..views_data_types import get_count_for_data_type

POST_GET = ("POST", "GET")

DATA_TYPE_NOT_REAL = "not_a_real_data_type"


class DataTypeTest(APITestCase):
    def test_data_type_list(self):
        r = self.client.get(reverse("data-type-list"))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertEqual(len(c), len(DATA_TYPES))
        ids = [dt["id"] for dt in c]
        self.assertIn(DATA_TYPE_EXPERIMENT, ids)
        # self.assertIn(DATA_TYPE_MCODEPACKET, ids)
        self.assertIn(DATA_TYPE_PHENOPACKET, ids)
        self.assertIn(DATA_TYPE_READSET, ids)
        self.assertIn(DATA_TYPE_EXPERIMENT_RESULT, ids)

    def test_data_type_list_non_uuid_project(self):
        # Non-UUID project
        r = self.client.get(reverse("data-type-list"), {"project": "a"})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_data_type_list_non_uuid_dataset(self):
        # Non-UUID dataset
        r = self.client.get(reverse("data-type-list"), {"dataset": "a"})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_data_type_detail(self):
        self.maxDiff = None
        r = self.client.get(reverse("data-type-detail", kwargs={"data_type": DATA_TYPE_PHENOPACKET}))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertDictEqual(c, {
            "id": DATA_TYPE_PHENOPACKET,
            "label": "Clinical Data",
            **DATA_TYPES[DATA_TYPE_PHENOPACKET],
            "queryable": True,
            "count": 0,
            "last_ingested": None,
        })

    def test_data_type_detail_non_uuid_project(self):
        # Non-UUID project
        r = self.client.get(reverse("data-type-detail", kwargs={"data_type": DATA_TYPE_PHENOPACKET}), {"project": "a"})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        r = self.client.get(
            reverse("data-type-detail", kwargs={"data_type": DATA_TYPE_EXPERIMENT_RESULT}), {"project": "a"})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_data_type_detail_non_uuid_dataset(self):
        # Non-UUID dataset
        r = self.client.get(reverse("data-type-detail", kwargs={"data_type": DATA_TYPE_PHENOPACKET}), {"dataset": "a"})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        r = self.client.get(reverse(
            "data-type-detail", kwargs={"data_type": DATA_TYPE_EXPERIMENT_RESULT}), {"dataset": "a"})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_data_type_detail_bad_data_type_for_count(self):
        r = self.client.get(reverse("data-type-detail", kwargs={"data_type": DATA_TYPE_READSET}))
        self.assertIsNone(r.json()["count"])

    async def test_data_type_count_bad_data_type(self):
        with self.assertRaises(ValueError):
            await get_count_for_data_type(DATA_TYPE_NOT_REAL)

    def test_data_type_detail_404(self):
        r = self.client.get(reverse("data-type-detail", kwargs={"data_type": DATA_TYPE_NOT_REAL}))
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)
        r.json()  # assert json response

    def test_data_type_schema(self):
        r = self.client.get(reverse("data-type-schema", kwargs={"data_type": DATA_TYPE_PHENOPACKET}))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertDictEqual(c, DATA_TYPES[DATA_TYPE_PHENOPACKET]["schema"])

    def test_data_type_schema_404(self):
        r = self.client.get(reverse("data-type-schema", kwargs={"data_type": DATA_TYPE_NOT_REAL}))
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)
        r.json()  # assert json response

    def test_data_type_metadata_schema(self):
        r = self.client.get(reverse("data-type-metadata-schema", kwargs={"data_type": DATA_TYPE_PHENOPACKET}))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertDictEqual(c, DATA_TYPES[DATA_TYPE_PHENOPACKET]["metadata_schema"])

    def test_data_type_metadata_schema_404(self):
        r = self.client.get(reverse("data-type-metadata-schema", kwargs={"data_type": DATA_TYPE_NOT_REAL}))
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)
        r.json()  # assert json response
