from django.http.request import HttpRequest
from rest_framework.request import Request as DrfRequest

from chord_metadata_service.authz.viewset import BentoAuthzScopedModelGenericListViewSet
from chord_metadata_service.chord.tests.helpers import ProjectTestCase
from chord_metadata_service.phenopackets import models as ph_m
from chord_metadata_service.phenopackets.tests import constants as ph_c


class TestNotImplViewSet(BentoAuthzScopedModelGenericListViewSet):
    pass


class AuthzBaseViewsetTest(ProjectTestCase):

    def setUp(self):
        super().setUp()
        self.individual = ph_m.Individual.objects.create(**ph_c.VALID_INDIVIDUAL_1)

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

        self.assertFalse(await TestNotImplViewSet.obj_is_in_request_scope(mock_drf_req, self.individual))

        mock_req_2 = HttpRequest()
        mock_req_2.GET["project"] = "does-not-exist"
        mock_drf_req_2 = DrfRequest(mock_req_2)

        self.assertFalse(await TestNotImplViewSet.obj_is_in_request_scope(mock_drf_req_2, self.individual))
