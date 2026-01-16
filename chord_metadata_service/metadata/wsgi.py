"""
WSGI config for metadata project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import structlog.stdlib
import os

from django.conf import settings
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chord_metadata_service.metadata.settings")

logger = structlog.stdlib.get_logger("katsu.wsgi")

# debugger section
if settings.DEBUG:
    try:
        import debugpy

        DEBUGGER_PORT = int(os.environ.get("DEBUGGER_PORT", 5678))
        debugpy.listen(("0.0.0.0", DEBUGGER_PORT))
        logger.info("debugger attached")
    except ImportError:
        logger.info("module debugpy not found. install to enable debugging with VS Code")
# end debugger section

application = get_wsgi_application()
