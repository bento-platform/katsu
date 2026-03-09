import uuid

from rest_framework import status
from rest_framework.reverse import reverse

from chord_metadata_service.authz.tests.helpers import AuthzAPITestCase
from chord_metadata_service.chord.ingest import WORKFLOW_INGEST_FUNCTION_MAP
from chord_metadata_service.chord.models import Dataset
from chord_metadata_service.chord.tests.constants import valid_dataset_1, VALID_PROJECT_2, valid_dataset_2
from chord_metadata_service.chord.tests.helpers import AuthzAPITestCaseWithProjectJSON
from chord_metadata_service.chord.workflows.metadata import WORKFLOW_PHENOPACKETS_JSON
from chord_metadata_service.logger import logger
from chord_metadata_service.restapi.tests.constants import VALID_PHENOPACKET_1
from ..models import Resource
from ..serializers import ResourceSerializer
from .constants import VALID_RESOURCE_1, VALID_RESOURCE_2, DUPLICATE_RESOURCE_3


class CreateResourceTest(AuthzAPITestCase):
    def setUp(self):
        self.resource = VALID_RESOURCE_2
        self.duplicate_resource = DUPLICATE_RESOURCE_3

    def test_create_resource(self):
        response = self.one_authz_post(reverse("resource-list"), json=self.resource)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Resource.objects.count(), 1)

    def test_create_resource_forbidden(self):
        response = self.one_no_authz_post(reverse("resource-list"), json=self.resource)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Resource.objects.count(), 0)

    def test_serializer(self):
        serializer = ResourceSerializer(data=self.resource)
        self.assertEqual(serializer.is_valid(), True)


class ListResourceTest(AuthzAPITestCaseWithProjectJSON):
    def setUp(self):
        super().setUp()
        self.url = reverse("resource-list")
        self.url_with_proj = f"{self.url}?project={self.project['identifier']}"

        # dataset for project 1
        r = self.one_authz_post(reverse("dataset-list"), json=valid_dataset_1(self.project["identifier"]))
        self.dataset = r.json()
        self.url_with_proj_ds = f"{self.url}?project={self.project['identifier']}&dataset={self.dataset['identifier']}"

        # project 2
        r = self.one_authz_post(reverse("project-list"), json=VALID_PROJECT_2)
        self.project_2 = r.json()

        #  - dataset for project 2
        r = self.one_authz_post(reverse("dataset-list"), json=valid_dataset_2(self.project_2["identifier"]))
        self.dataset_2 = r.json()

    def test_list_resources_basic(self):
        self.one_authz_post(self.url, json=VALID_RESOURCE_1)
        self.one_authz_post(self.url, json=VALID_RESOURCE_2)

        res = self.one_authz_get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()["results"]), 2)

        # check that we don't have any resources under the project (until later tests...)
        res = self.one_authz_get(self.url_with_proj)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()["results"]), 0)

    def test_list_resources_scope_dne(self):
        res = self.one_authz_get(f"{self.url}?project=does-not-exist")
        # non-UUID - triggers scope error when handling permissions:
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        res = self.one_authz_get(f"{self.url}?project={uuid.uuid4()}")
        # does not exist - triggers scope error when handling permissions:
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_resources_forbidden(self):
        response = self.one_no_authz_get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.one_no_authz_get(self.url_with_proj)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_resources_project_dataset(self):
        r = Resource.objects.create(**VALID_RESOURCE_1)
        Resource.objects.create(**VALID_RESOURCE_2)  # r2

        ds = Dataset.objects.get(pk=self.dataset["identifier"])
        ds.additional_resources.add(r)

        subtests = [
            (self.url, 2),
            (self.url_with_proj, 1),
            (f"{self.url}?project={self.project_2['identifier']}", 0),
            (self.url_with_proj_ds, 1),
            (f"{self.url}?project={self.project_2['identifier']}&dataset={self.dataset_2['identifier']}", 0),
        ]

        for subtest in subtests:
            with self.subTest(params=subtest):
                res = self.one_authz_get(subtest[0])
                self.assertEqual(res.status_code, status.HTTP_200_OK)
                self.assertEqual(len(res.json()["results"]), subtest[1])

    def test_list_resources_dataset_and_phenopacket(self):
        r = Resource.objects.create(**VALID_RESOURCE_1)

        ds = Dataset.objects.get(pk=self.dataset["identifier"])
        ds.additional_resources.add(r)

        pd = {
            **VALID_PHENOPACKET_1,
            "dataset": self.dataset["identifier"],
            "meta_data": {**VALID_PHENOPACKET_1["meta_data"], "resources": [VALID_RESOURCE_2]},
        }

        # create phenopacket associated with the dataset (+ a new resource in the phenopacket metadata)
        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](pd, ds.identifier, logger)

        # first, check we get all the resources back successfully with no scoping
        res = self.one_authz_get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()["results"]), 2)

        # then, check if we scope in that we correctly get both paths to the dataset resources

        res = self.one_authz_get(self.url_with_proj)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()["results"]), 2)

        res = self.one_authz_get(self.url_with_proj_ds)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()["results"]), 2)
