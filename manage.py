#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chord_metadata_service.metadata.settings")
    if "test" in sys.argv:
        os.environ["DJANGO_SETTINGS_MODULE"] = "chord_metadata_service.metadata.test_settings"

        # monkeypatch aioresponses compatibility for aiohttp 3.14+
        # see https://github.com/j7an/dep-rank/blob/9ce06c5bc039675bb12c2b9da0766fa1e4c654dd/tests/conftest.py#L14-L30
        # TODO: switch to aiointercept

        import inspect
        from unittest.mock import Mock

        import aiohttp

        _response_init = aiohttp.ClientResponse.__init__
        if "stream_writer" in inspect.signature(_response_init).parameters:

            def _patched_response_init(self, *args, **kwargs):  # type: ignore[no-untyped-def]
                kwargs.setdefault("stream_writer", Mock(output_size=0))
                _response_init(self, *args, **kwargs)

            aiohttp.ClientResponse.__init__ = _patched_response_init

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
