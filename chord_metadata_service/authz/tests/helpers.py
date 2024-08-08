from ..types import DataPermissionsDict
from aioresponses import aioresponses
from bento_lib.auth.types import EvaluationResultMatrix
from rest_framework.test import APITestCase
from typing import Literal


__all__ = [
    "mock_authz_eval_one_result",
    "mock_authz_eval_result",
    "DTAccessLevel",
    "AuthzAPITestCase",
    "PermissionsTestCaseMixin",
]


def mock_authz_eval_one_result(m: aioresponses, result: bool):
    m.post("http://authz.local/policy/evaluate", payload={"result": [[result]]})


def mock_authz_eval_result(m: aioresponses, result: EvaluationResultMatrix | list[list[bool]]):
    m.post("http://authz.local/policy/evaluate", payload={"result": result})


DTAccessLevel = Literal["none", "bool", "counts", "full"]


class AuthzAPITestCase(APITestCase):
    # data type permissions: bool, counts, data
    dt_none_eval_res = [[False, False, False]]
    dt_bool_eval_res = [[True, False, False]]
    dt_counts_eval_res = [[True, True, False]]
    dt_full_eval_res = [[True, True, True]]

    dt_levels: dict[DTAccessLevel, list[list[bool]]] = {
        "none": dt_none_eval_res,
        "bool": dt_bool_eval_res,
        "counts": dt_counts_eval_res,
        "full": dt_full_eval_res,
    }

    def dt_get(self, level: Literal["none", "bool", "counts", "full"], u: str, *args, **kwargs):
        with aioresponses() as m:
            mock_authz_eval_result(m, self.dt_levels[level])  # data type permissions: bool, counts, data
            return self.client.get(u, *args, **kwargs)

    def dt_post(self, level: Literal["none", "bool", "counts", "full"], u: str, *args, **kwargs):
        with aioresponses() as m:
            mock_authz_eval_result(m, self.dt_levels[level])  # data type permissions: bool, counts, data
            return self.client.post(u, *args, **kwargs)

    def dt_authz_none_get(self, u: str, *args, **kwargs):
        return self.dt_get("none", u, *args, **kwargs)

    def dt_authz_bool_get(self, u: str, *args, **kwargs):
        return self.dt_get("bool", u, *args, **kwargs)

    def dt_authz_counts_get(self, u: str, *args, **kwargs):
        return self.dt_get("counts", u, *args, **kwargs)

    def dt_authz_full_get(self, u: str, *args, **kwargs):
        return self.dt_get("full", u, *args, **kwargs)

    def dt_authz_full_post(self, u: str, *args, **kwargs):
        return self.dt_post("full", u, *args, **kwargs)


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
