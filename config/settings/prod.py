#####################################################################
#                   PRODUCTION SETTINGS                             #
# Inherit from setting dev.py. Contain only necessary settings to   #
# make the project run. Following:                                  #
# https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/ #
#####################################################################

from .dev import *

# remove dev settings
DEBUG = False
INSTALLED_APPS.remove("debug_toolbar")
MIDDLEWARE.remove("debug_toolbar.middleware.DebugToolbarMiddleware")
ALLOWED_HOSTS = [
    "candig.docker.internal",
    os.environ.get("HOST_CONTAINER_NAME"),
]

# Override the log level for handlers and loggers
LOGGING["handlers"]["console"]["level"] = "ERROR"
LOGGING["handlers"]["file"]["level"] = "ERROR"
LOGGING["loggers"][""]["level"] = "ERROR"

# ==============================================================================
# SECURITY SETTINGS
# ==============================================================================
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_SSL_REDIRECT = True # need port 443
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 60  # Once confirm that all assets are served securely(i.e. HSTS didn’t break anything), increase this value
# SECURE_HSTS_SECONDS = 60 * 60 * 24 * 7 * 52  # one year

