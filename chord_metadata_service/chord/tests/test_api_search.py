from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

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
