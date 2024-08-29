import uuid

from django.urls import reverse
from rest_framework import status

from chord_metadata_service.authz.tests.helpers import AuthzAPITestCase, PermissionsTestCaseMixin
from chord_metadata_service.discovery.tests.constants import DISCOVERY_CONFIG_TEST
from chord_metadata_service.phenopackets.tests.helpers import PhenoTestCase

from ..data_types import DATA_TYPE_EXPERIMENT, DATA_TYPE_PHENOPACKET, DATA_TYPES
from ..views_data_types import get_count_for_data_type

POST_GET = ("POST", "GET")

DATA_TYPE_NOT_REAL = "not_a_real_data_type"


class DataTypeHelperTest(PhenoTestCase, PermissionsTestCaseMixin):
    @staticmethod
    async def get_count_for_phenopackets(permissions, project=None, dataset=None):
        return await get_count_for_data_type(
            DATA_TYPE_PHENOPACKET, project, dataset, DISCOVERY_CONFIG_TEST, permissions
        )

    async def test_data_type_count(self):
        self.assertEqual(await self.get_count_for_phenopackets(self.permissions_full), 1)

    async def test_data_type_count_censored(self):
        self.assertEqual(await self.get_count_for_phenopackets(self.permissions_counts), 0)  # censored
        self.assertEqual(await self.get_count_for_phenopackets(self.permissions_bool), 0)  # censored
        self.assertEqual(await self.get_count_for_phenopackets(self.permissions_none), 0)  # censored

    async def test_data_type_count_bad_project_id(self):
        with self.assertRaises(ValueError):
            await self.get_count_for_phenopackets(self.permissions_full, project="not-uuid")

        with self.assertRaises(ValueError):
            await self.get_count_for_phenopackets(self.permissions_full, project="not-uuid", dataset=str(uuid.uuid4()))

    async def test_data_type_count_bad_dataset_id(self):
        with self.assertRaises(ValueError):
            await self.get_count_for_phenopackets(self.permissions_full, project=str(uuid.uuid4()), dataset="not-uuid")

        with self.assertRaises(ValueError):
            await self.get_count_for_phenopackets(self.permissions_full, project=None, dataset="not-uuid")

    async def test_data_type_count_bad_data_type(self):
        with self.assertRaises(ValueError):
            await get_count_for_data_type(
                DATA_TYPE_NOT_REAL, None, None, DISCOVERY_CONFIG_TEST, self.permissions_full
            )


class DataTypeTest(AuthzAPITestCase, PermissionsTestCaseMixin):
    def test_data_type_list(self):
        r = self.dt_authz_counts_get(reverse("data-type-list"))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertEqual(len(c), len(DATA_TYPES))
        ids = [dt["id"] for dt in c]
        self.assertIn(DATA_TYPE_EXPERIMENT, ids)
        self.assertIn(DATA_TYPE_PHENOPACKET, ids)

    def test_data_type_list_non_uuid_project(self):
        # Non-UUID project
        r = self.dt_authz_counts_get(reverse("data-type-list"), {"project": "a"})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_data_type_list_non_uuid_dataset(self):
        # Non-UUID dataset
        r = self.dt_authz_counts_get(reverse("data-type-list"), {"dataset": "a"})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_data_type_detail(self):
        # counts permission
        r = self.dt_authz_counts_get(reverse("data-type-detail", kwargs={"data_type": DATA_TYPE_PHENOPACKET}))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertDictEqual(r.json(), {
            "id": DATA_TYPE_PHENOPACKET,
            "label": "Clinical Data",
            **DATA_TYPES[DATA_TYPE_PHENOPACKET],
            "queryable": True,
            "count": 0,
            "last_ingested": None,
        })

    def test_data_type_detail_no_counts(self):
        kwargs = {"data_type": DATA_TYPE_PHENOPACKET}
        expected_res = {
            "id": DATA_TYPE_PHENOPACKET,
            "label": "Clinical Data",
            **DATA_TYPES[DATA_TYPE_PHENOPACKET],
            "queryable": True,
            "last_ingested": None,
        }

        # bool permission - no counts
        r = self.dt_authz_bool_get(reverse("data-type-detail", kwargs=kwargs))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertDictEqual(r.json(), expected_res)

        # no data permissions - no counts
        r = self.dt_authz_none_get(reverse("data-type-detail", kwargs=kwargs))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertDictEqual(r.json(), expected_res)

    def test_data_type_detail_non_uuid_project(self):
        # Non-UUID project
        r = self.dt_authz_counts_get(
            reverse("data-type-detail", kwargs={"data_type": DATA_TYPE_PHENOPACKET}), {"project": "a"})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_data_type_detail_non_uuid_dataset(self):
        # Non-UUID dataset
        r = self.dt_authz_counts_get(
            reverse("data-type-detail", kwargs={"data_type": DATA_TYPE_PHENOPACKET}), {"dataset": "a"})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_data_type_detail_404(self):
        r = self.dt_authz_counts_get(reverse("data-type-detail", kwargs={"data_type": DATA_TYPE_NOT_REAL}))
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
