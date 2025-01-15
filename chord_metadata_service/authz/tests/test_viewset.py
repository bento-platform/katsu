import uuid

from aioresponses import aioresponses
from django.http.request import HttpRequest
from rest_framework.request import Request as DrfRequest

from chord_metadata_service.authz.tests.helpers import AuthzAPITestCase
from chord_metadata_service.authz.viewset import BentoAuthzScopedModelGenericListViewSet
from chord_metadata_service.chord.tests.helpers import ProjectTestCase
from chord_metadata_service.discovery.exceptions import DiscoveryScopeException
from chord_metadata_service.phenopackets import models as ph_m
from chord_metadata_service.phenopackets.tests import constants as ph_c


class TestNotImplViewSet(BentoAuthzScopedModelGenericListViewSet):
    pass


class AuthzBaseViewsetTest(AuthzAPITestCase, ProjectTestCase):

    def setUp(self):
        super().setUp()
        self.individual = ph_m.Individual.objects.create(**ph_c.VALID_INDIVIDUAL_1)

        self.mock_project_req = HttpRequest()
        self.mock_project_req.GET["project"] = str(self.project.identifier)
        self.mock_project_drf_req = DrfRequest(self.mock_project_req)

    def test_get_queryset_not_impl(self):
        with self.assertRaises(NotImplementedError):
            TestNotImplViewSet().get_queryset()

    def test_permission_from_request_none(self):
        vs = TestNotImplViewSet()
        vs.action = "fubar"
        mock_drf_req = DrfRequest(HttpRequest())
        self.assertIsNone(vs.permission_from_request(mock_drf_req))

    async def test_obj_is_in_request_scope(self):
        mock_req = HttpRequest()
        mock_req.GET["project"] = "does-not-exist"
        mock_drf_req = DrfRequest(mock_req)

        with self.assertRaises(DiscoveryScopeException):
            await TestNotImplViewSet.obj_is_in_request_scope(mock_drf_req, self.individual)

        mock_req_2 = HttpRequest()
        mock_req_2.GET["project"] = str(uuid.uuid4())
        mock_drf_req_2 = DrfRequest(mock_req_2)

        with self.assertRaises(DiscoveryScopeException):
            await TestNotImplViewSet.obj_is_in_request_scope(mock_drf_req_2, self.individual)

    async def test_request_has_data_type_permissions(self):
        vs = TestNotImplViewSet()
        vs.action = "list"
        with aioresponses() as m:
            self.mock_authz_eval_one_result(m, True)
            self.assertTrue(await vs.request_has_data_type_permissions(self.mock_project_drf_req, None))

    async def test_request_has_data_type_permissions_false(self):
        vs = TestNotImplViewSet()
        vs.action = "list"
        with aioresponses() as m:
            self.mock_authz_eval_one_result(m, False)
            self.assertFalse(await vs.request_has_data_type_permissions(self.mock_project_drf_req, None))

    async def test_request_has_data_type_permissions_action_dne(self):
        vs = TestNotImplViewSet()
        vs.action = "does-not-exist"  # no permissions implemented for this action
        self.assertFalse(await vs.request_has_data_type_permissions(self.mock_project_drf_req, None))

    async def test_request_has_data_type_permissions_scope_dne(self):
        mock_req = HttpRequest()
        mock_req.GET["project"] = "does-not-exist"
        mock_drf_req = DrfRequest(mock_req)

        vs = TestNotImplViewSet()

        with self.assertRaises(DiscoveryScopeException):
            await vs.request_has_data_type_permissions(mock_drf_req, None)

        mock_req_2 = HttpRequest()
        mock_req_2.GET["project"] = str(uuid.uuid4())
        mock_drf_req_2 = DrfRequest(mock_req_2)

        with self.assertRaises(DiscoveryScopeException):
            await vs.request_has_data_type_permissions(mock_drf_req_2, None)
