from django.http.request import HttpRequest
from django.test import TestCase
from rest_framework.request import Request as DrfRequest

from chord_metadata_service.authz.viewset import BentoAuthzScopedModelGenericListViewSet


class TestNotImplViewSet(BentoAuthzScopedModelGenericListViewSet):
    pass


class AuthzBaseViewsetTest(TestCase):

    def test_get_queryset_not_impl(self):
        with self.assertRaises(NotImplementedError):
            TestNotImplViewSet().get_queryset()

    def test_permission_from_request_none(self):
        vs = TestNotImplViewSet()
        vs.action = "fubar"
        mock_req = DrfRequest(HttpRequest())
        self.assertIsNone(vs.permission_from_request(mock_req))
