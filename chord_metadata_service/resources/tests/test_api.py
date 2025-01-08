import uuid

from rest_framework import status
from rest_framework.reverse import reverse

from chord_metadata_service.authz.tests.helpers import AuthzAPITestCase
from chord_metadata_service.chord.tests.helpers import AuthzAPITestCaseWithProjectJSON
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
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        res = self.one_authz_get(f"{self.url}?project={uuid.uuid4()}")
        # does not exist - triggers scope error when handling permissions:
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_resources_forbidden(self):
        response = self.one_no_authz_get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.one_no_authz_get(self.url_with_proj)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
