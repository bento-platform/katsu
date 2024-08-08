import uuid

from django.urls import reverse
from django.test import TestCase
from rest_framework import status

from chord_metadata_service.authz.tests.helpers import AuthzAPITestCase, PermissionsTestCaseMixin
from chord_metadata_service.discovery.tests.constants import DISCOVERY_CONFIG_TEST
from chord_metadata_service.patients import models as pa_m
from chord_metadata_service.phenopackets.tests import constants as ph_c
from chord_metadata_service.phenopackets import models as ph_m

from ..data_types import DATA_TYPE_EXPERIMENT, DATA_TYPE_PHENOPACKET, DATA_TYPES
from ..models import Project, Dataset
from ..views_data_types import get_count_for_data_type
from .constants import VALID_DATA_USE_1

POST_GET = ("POST", "GET")

DATA_TYPE_NOT_REAL = "not_a_real_data_type"


class DataTypeHelperTest(TestCase, PermissionsTestCaseMixin):
    def setUp(self):
        p = Project.objects.create(title="Project 1", description="")
        d = Dataset.objects.create(title="Dataset 1", description="Some dataset", data_use=VALID_DATA_USE_1, project=p)

        self.individual_1 = pa_m.Individual.objects.create(**ph_c.VALID_INDIVIDUAL_1)
        self.meta_data = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_1)
        self.phenopacket = ph_m.Phenopacket.objects.create(
            id="phenopacket_id:1",
            subject=self.individual_1,
            dataset=d,
            meta_data=self.meta_data,
        )

    async def test_data_type_count(self):
        self.assertEqual(
            await get_count_for_data_type(
                DATA_TYPE_PHENOPACKET,
                None,
                None,
                DISCOVERY_CONFIG_TEST,
                self.permissions_full,
            ),
            1
        )

    async def test_data_type_count_censored(self):
        self.assertEqual(
            await get_count_for_data_type(
                DATA_TYPE_PHENOPACKET,
                None,
                None,
                DISCOVERY_CONFIG_TEST,
                self.permissions_counts,
            ),
            0  # censored
        )

    async def test_data_type_count_bad_project_id(self):
        with self.assertRaises(ValueError):
            await get_count_for_data_type(
                DATA_TYPE_PHENOPACKET,
                "not-uuid",
                None,
                DISCOVERY_CONFIG_TEST,
                self.permissions_full,
            )

        with self.assertRaises(ValueError):
            await get_count_for_data_type(
                DATA_TYPE_PHENOPACKET,
                "not-uuid",
                str(uuid.uuid4()),
                DISCOVERY_CONFIG_TEST,
                self.permissions_full,
            )

    async def test_data_type_count_bad_dataset_id(self):
        with self.assertRaises(ValueError):
            await get_count_for_data_type(
                DATA_TYPE_PHENOPACKET,
                str(uuid.uuid4()),
                "not-uuid",
                DISCOVERY_CONFIG_TEST,
                self.permissions_full,
            )

        with self.assertRaises(ValueError):
            await get_count_for_data_type(
                DATA_TYPE_PHENOPACKET,
                None,
                "not-uuid",
                DISCOVERY_CONFIG_TEST,
                self.permissions_full,
            )

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
        # bool permission - no counts
        r = self.dt_authz_bool_get(reverse("data-type-detail", kwargs={"data_type": DATA_TYPE_PHENOPACKET}))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertDictEqual(r.json(), {
            "id": DATA_TYPE_PHENOPACKET,
            "label": "Clinical Data",
            **DATA_TYPES[DATA_TYPE_PHENOPACKET],
            "queryable": True,
            "last_ingested": None,
        })

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
