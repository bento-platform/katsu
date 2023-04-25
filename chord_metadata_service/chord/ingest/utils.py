from __future__ import annotations

import contextlib
import os
import re
import requests
import shutil
import tempfile

from bento_lib.drs.utils import get_access_method_of_type, fetch_drs_record_by_uri
from django.conf import settings
from urllib.parse import urlparse

from typing import Any, Callable

from chord_metadata_service.logger import logger
from .exceptions import IngestError

__all__ = [
    "map_if_list",
    "get_output_or_raise",
    "query_and_check_nulls",
    "workflow_file_output_to_path",
]

DRS_URI_SCHEME = "drs"
FILE_URI_SCHEME = "file"
HTTP_URI_SCHEME = "http"
HTTPS_URI_SCHEME = "https"

WINDOWS_DRIVE_SCHEME = re.compile(r"^[a-zA-Z]$")


def map_if_list(fn: Callable, data: Any, *args, **kwargs) -> Any:
    # TODO: Any sequence?
    return (
        [fn(d, *args, idx=idx, **kwargs) for idx, d in enumerate(data)] if isinstance(data, list)
        else fn(data, *args, **kwargs)
    )


def get_output_or_raise(workflow_outputs, key):
    if key not in workflow_outputs:
        raise IngestError(f"Missing workflow output: {key}")

    return workflow_outputs[key]


def query_and_check_nulls(obj: dict, key: str, transform: Callable = lambda x: x):
    value = obj.get(key)
    return {f"{key}__isnull": True} if value is None else {key: transform(value)}


def workflow_http_download(tmp_dir: str, http_uri: str) -> str:
    # TODO: Sanity check: no external insecure HTTP calls
    # TODO: Disable HTTPS cert check in debug mode
    # TODO: Handle response exceptions

    r = requests.get(http_uri)

    if not r.ok:
        err = f"HTTP error encountered while downloading ingestion URI: {http_uri}"
        logger.error(f"{err} (Status: {r.status_code}; Contents: {r.content.decode('utf-8')})")
        raise IngestError(err)

    data_path = f"{tmp_dir}ingest_download_data"

    with open(data_path, "wb") as df:
        df.write(r.content)

    return data_path


@contextlib.contextmanager
def workflow_file_output_to_path(file_uri_or_path: str):
    # TODO: Should be able to download from DRS instead of using file URIs directly

    parsed_file_uri = urlparse(file_uri_or_path)

    if WINDOWS_DRIVE_SCHEME.match(parsed_file_uri.scheme):
        # In Windows, file paths can start with c:/ or similar (which is the drive letter.) This will get handled
        # as a 'scheme' by urlparse, so we use a regex to detect Windows-style drive 'schemes'.
        yield file_uri_or_path
        return

    if parsed_file_uri.scheme in (FILE_URI_SCHEME, ""):
        # File URI, or file path with no URI scheme (in which case implicitly assume a 'file://' in front)
        yield parsed_file_uri.path
        return

    # From here on out, we're dealing with downloads - check to make sure we
    # have somewhere to put the temporary files.

    should_del = False
    tmp_dir = settings.SERVICE_TEMP

    if tmp_dir is None:
        tmp_dir = tempfile.mkdtemp()
        should_del = True

    if not os.access(tmp_dir, os.W_OK):
        raise IngestError(f"Directory does not exist or is not writable: {tmp_dir}")

    try:
        tmp_dir = tmp_dir.rstrip("/") + "/"

        if parsed_file_uri.scheme == DRS_URI_SCHEME:  # DRS object URI
            drs_obj = fetch_drs_record_by_uri(file_uri_or_path, settings.DRS_URL)

            file_access = get_access_method_of_type(drs_obj, "file")
            if file_access:
                yield urlparse(file_access["access_url"]["url"]).path
                return

            # TODO: Some mechanism to do this with auth
            http_access = get_access_method_of_type(drs_obj, "http")
            if http_access:
                # TODO: Handle DRS headers field if available - how to do this with grace and compatibility with
                #  Bento's auth system?
                yield workflow_http_download(tmp_dir, http_access["access_url"]["url"])
                return

            # If we get here, we have a DRS object we cannot handle; raise an error.
            raise IngestError(f"Cannot handle DRS object {file_uri_or_path}: No file or http access methods")

        elif parsed_file_uri.scheme in (HTTP_URI_SCHEME, HTTPS_URI_SCHEME):
            yield workflow_http_download(tmp_dir, file_uri_or_path)

        else:
            # If we get here, we have a scheme we cannot handle; raise an error.
            raise IngestError(f"Cannot handle workflow output URI scheme: {parsed_file_uri.scheme}")

    finally:
        # Clean up the temporary directory if necessary
        if should_del and tmp_dir:
            shutil.rmtree(tmp_dir)
