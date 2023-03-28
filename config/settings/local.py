from .base import *

DEBUG = True

FAKE_AUTHORIZED_DATASETS = ["SYNTHETIC-1"]

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# LOCAL SETTINGS
KATSU_AUTHORIZATION = "LOCAL_SETTING_NO_AUTH"
CANDIG_OPA_URL = "LOCAL_SETTING_NO_OPA_URL"
CANDIG_OPA_SITE_ADMIN_KEY = "LOCAL_SETTING_NO_SITE_ADMIN_KEY"
CANDIG_OPA_SECRET = "LOCAL_SETTING_NO_OPA_SECRET"

INSTALLED_APPS.append("debug_toolbar")

MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "katsu_local",
        "USER": "admin_local",
        "PASSWORD": "password_local",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

# Debug toolbar settings

if DEBUG:
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + [
        "127.0.0.1",
        "10.0.2.2",
    ]
