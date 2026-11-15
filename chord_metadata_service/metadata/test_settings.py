import inspect
from unittest.mock import Mock

import aiohttp

from .settings import *  # noqa: F401, F403

# Tests are run locally with the Django dev server. Adding a sub-path which
# is managed by the gateway in production, creates wrong references and breaks
# almost every test. This resets the setting for when an environment variable
# CHORD_METADATA_SUB_PATH had been set.
FORCE_SCRIPT_NAME = ""

# monkeypatch aioresponses compatibility for aiohttp 3.14+
# see https://github.com/j7an/dep-rank/blob/9ce06c5bc039675bb12c2b9da0766fa1e4c654dd/tests/conftest.py#L14-L30
# This lives here, not in manage.py, so that `test --parallel` workers started with spawn/forkserver (the default on
# Python 3.14) also get it: each worker imports the settings module again in django.setup().
# TODO: switch to aiointercept

_response_init = aiohttp.ClientResponse.__init__
if "stream_writer" in inspect.signature(_response_init).parameters:

    def _patched_response_init(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        kwargs.setdefault("stream_writer", Mock(output_size=0))
        _response_init(self, *args, **kwargs)

    aiohttp.ClientResponse.__init__ = _patched_response_init
