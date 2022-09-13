"""
WSGI config for metadata project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
import logging

from django.core.wsgi import get_wsgi_application
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chord_metadata_service.metadata.settings')

logger = logging.getLogger(__name__)

# debugger section
if settings.DEBUG:
    try:
        import debugpy
        DEBUGGER_PORT = int(os.environ.get('DEBUGGER_PORT', 5678))
        debugpy.listen(("0.0.0.0", DEBUGGER_PORT))
        logger.info('Debugger Attached')
    except ImportError:
        logger.info("Module debugpy not found. Install to enable debugging with VS-Code")
# end debugger section

application = get_wsgi_application()
