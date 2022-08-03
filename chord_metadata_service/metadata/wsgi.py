"""
WSGI config for metadata project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chord_metadata_service.metadata.settings')

# debugger section
if settings.DEBUG:
    import debugpy
    DEBUGGER_PORT = int(os.environ.get('DEBUGGER_PORT', 5678))
    debugpy.listen(("0.0.0.0", DEBUGGER_PORT))
    print('Attached')
# end debugger section

application = get_wsgi_application()
