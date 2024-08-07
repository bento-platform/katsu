from ..types import DataPermissionsDict
from aioresponses import aioresponses
from bento_lib.auth.types import EvaluationResultMatrix
from rest_framework.test import APITestCase


__all__ = [
    "mock_authz_eval_one_result",
    "mock_authz_eval_result",
    "AuthzAPITestCase",
    "PermissionsTestCaseMixin",
]


def mock_authz_eval_one_result(m: aioresponses, result: bool):
    m.post("http://authz.local/policy/evaluate", payload={"result": [[result]]})


def mock_authz_eval_result(m: aioresponses, result: EvaluationResultMatrix | list[list[bool]]):
    m.post("http://authz.local/policy/evaluate", payload={"result": result})


class AuthzAPITestCase(APITestCase):
    dt_counts_eval_res = [[True, True, False]]
    dt_full_eval_res = [[True, True, True]]

    def dt_authz_counts_get(self, u: str, *args, **kwargs):
        with aioresponses() as m:
            mock_authz_eval_result(m, self.dt_counts_eval_res)  # data type permissions: bool, counts, data
            return self.client.get(u, *args, **kwargs)

    def dt_authz_full_get(self, u: str, *args, **kwargs):
        with aioresponses() as m:
            mock_authz_eval_result(m, self.dt_full_eval_res)  # data type permissions: bool, counts, data
            return self.client.get(u, *args, **kwargs)

    def dt_authz_full_post(self, u: str, *args, **kwargs):
        with aioresponses() as m:
            mock_authz_eval_result(m, self.dt_full_eval_res)  # data type permissions: bool, counts, data
            return self.client.post(u, *args, **kwargs)


class PermissionsTestCaseMixin:
    permissions_bool: DataPermissionsDict = {
        "bool_": True,
        "counts": False,
        "data": False,
    }
    permissions_counts: DataPermissionsDict = {
        "bool_": True,
        "counts": True,
        "data": False,
    }
    permissions_full: DataPermissionsDict = {
        "bool_": True,
        "counts": True,
        "data": True,
    }
