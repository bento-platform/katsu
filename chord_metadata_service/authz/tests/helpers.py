import json

from aiointercept import aiointercept
from bento_lib.auth.types import EvaluationResultMatrix
from rest_framework.test import APITransactionTestCase
from typing import Literal

from ..types import DataPermissions


__all__ = [
    "DTAccessLevel",
    "AuthzAPITestCase",
    "PermissionsTestCaseMixin",
]


DTAccessLevel = Literal["none", "bool", "counts", "full"]


class AuthzAPITestCase(APITransactionTestCase):
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

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def mock_authz_eval_one_result(m: aiointercept, result: bool):
        m.post("http://authz.local/policy/evaluate", payload={"result": [[result]]})

    @staticmethod
    def mock_authz_eval_result(m: aiointercept, result: EvaluationResultMatrix | list[list[bool]]):
        m.post("http://authz.local/policy/evaluate", payload={"result": result})

    # ------------------------------------------------------------------------------------------------------------------

    async def _one_authz_generic(
        self, method: Literal["get", "post", "put", "patch", "delete"], authz_res: bool, url: str, *args, **kwargs
    ):
        if "json" in kwargs:
            kwargs["data"] = json.dumps(kwargs["json"])
            del kwargs["json"]

        if method in ("post", "put", "patch") and "format" not in kwargs:
            kwargs["content_type"] = "application/json"

        async with aiointercept(mock_external_urls=True) as m:
            self.mock_authz_eval_one_result(m, authz_res)
            return await getattr(self.async_client, method)(url, *args, **kwargs)

    async def _one_authz_get(self, authz_res: bool, url: str, *args, **kwargs):
        return await self._one_authz_generic("get", authz_res, url, *args, **kwargs)

    async def one_authz_get(self, url: str, *args, **kwargs):
        """Mocks a single True response from the authorization service and executes a GET request."""
        return await self._one_authz_get(True, url, *args, **kwargs)

    async def one_no_authz_get(self, url: str, *args, **kwargs):
        """Mocks a single False response from the authorization service and executes a GET request."""
        return await self._one_authz_get(False, url, *args, **kwargs)

    async def _one_authz_post(self, authz_res: bool, url: str, *args, **kwargs):
        return await self._one_authz_generic("post", authz_res, url, *args, **kwargs)

    async def one_authz_post(self, url: str, *args, **kwargs):
        """Mocks a single True response from the authorization service and executes a JSON POST request."""
        return self._one_authz_post(True, url, *args, **kwargs)

    async def one_no_authz_post(self, url: str, *args, **kwargs):
        """Mocks a single False response from the authorization service and executes a JSON POST request."""
        return self._one_authz_post(False, url, *args, **kwargs)

    async def _one_authz_put(self, authz_res: bool, url: str, *args, **kwargs):
        return self._one_authz_generic("put", authz_res, url, *args, **kwargs)

    async def one_authz_put(self, url: str, *args, **kwargs):
        """Mocks a single True response from the authorization service and executes a JSON PUT request."""
        return self._one_authz_put(True, url, *args, **kwargs)

    async def one_no_authz_put(self, url: str, *args, **kwargs):
        """Mocks a single False response from the authorization service and executes a JSON PUT request."""
        return self._one_authz_put(False, url, *args, **kwargs)

    async def _one_authz_patch(self, authz_res: bool, url: str, *args, **kwargs):
        return self._one_authz_generic("patch", authz_res, url, *args, **kwargs)

    async def one_authz_patch(self, url: str, *args, **kwargs):
        """
        Mocks a single True response from the authorization service and executes a JSON PATCH request.
        """
        return self._one_authz_patch(True, url, *args, **kwargs)

    async def one_no_authz_patch(self, url: str, *args, **kwargs):
        """
        Mocks a single False response from the authorization service and executes a JSON PATCH request.
        """
        return self._one_authz_patch(False, url, *args, **kwargs)

    async def _one_authz_delete(self, authz_res: bool, url: str, *args, **kwargs):
        async with aiointercept(mock_external_urls=True) as m:
            self.mock_authz_eval_one_result(m, authz_res)
            return await self.async_client.delete(url, *args, **kwargs)

    async def _async_one_authz_delete(self, authz_res: bool, url: str, *args, **kwargs):
        async with aiointercept(mock_external_urls=True) as m:
            self.mock_authz_eval_one_result(m, authz_res)
            return await self.async_client.delete(url, *args, **kwargs)

    async def one_authz_delete(self, url: str, *args, **kwargs):
        """
        Mocks a single True response from the authorization service and executes a DELETE request.
        """
        return self._one_authz_delete(True, url, *args, **kwargs)

    async def async_one_authz_delete(self, url: str, *args, **kwargs):
        """
        Mocks a single True response from the authorization service and executes an asynchronous DELETE request.
        """
        return await self._async_one_authz_delete(True, url, *args, **kwargs)

    async def one_no_authz_delete(self, url: str, *args, **kwargs):
        """
        Mocks a single False response from the authorization service and executes a DELETE request.
        """
        return self._one_authz_delete(False, url, *args, **kwargs)

    # ------------------------------------------------------------------------------------------------------------------

    async def dt_get(self, level: Literal["none", "bool", "counts", "full"], url: str, *args, **kwargs):
        async with aiointercept(mock_external_urls=True) as m:
            self.mock_authz_eval_result(m, self.dt_levels[level])  # data type permissions: bool, counts, data
            # Some endpoints make a second authz call for dataset-level permissions.
            self.mock_authz_eval_result(m, self.dt_levels[level])
            return self.client.get(url, *args, **kwargs)

    async def dt_post(self, level: Literal["none", "bool", "counts", "full"], url: str, *args, **kwargs):
        async with aiointercept(mock_external_urls=True) as m:
            self.mock_authz_eval_result(m, self.dt_levels[level])  # data type permissions: bool, counts, data
            # Some endpoints make a second authz call for dataset-level permissions.
            self.mock_authz_eval_result(m, self.dt_levels[level])
            return self.client.post(url, *args, **kwargs)

    async def dt_authz_none_get(self, url: str, *args, **kwargs):
        return await self.dt_get("none", url, *args, **kwargs)

    async def dt_authz_bool_get(self, url: str, *args, **kwargs):
        return await self.dt_get("bool", url, *args, **kwargs)

    async def dt_authz_counts_get(self, url: str, *args, **kwargs):
        return await self.dt_get("counts", url, *args, **kwargs)

    async def dt_authz_counts_post(self, url: str, *args, **kwargs):
        return await self.dt_post("counts", url, *args, **kwargs)

    async def dt_authz_full_get(self, url: str, *args, **kwargs):
        return await self.dt_get("full", url, *args, **kwargs)

    async def dt_authz_full_post(self, url: str, *args, **kwargs):
        return await self.dt_post("full", url, *args, **kwargs)


class PermissionsTestCaseMixin:
    permissions_none: DataPermissions = DataPermissions(bool_=False, counts=False, data=False)
    permissions_bool: DataPermissions = DataPermissions(bool_=True, counts=False, data=False)
    permissions_counts: DataPermissions = DataPermissions(bool_=True, counts=True, data=False)
    permissions_full: DataPermissions = DataPermissions(bool_=True, counts=True, data=True)
