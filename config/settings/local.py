from .base import *

DEBUG = True

FAKE_AUTHORIZED_DATASETS = ["SYNTHETIC-POG"]

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

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

LOCAL_AUTHORIZED_DATASET = [
    {"username": "user1", "datasets": ["SYNTHETIC-POG"]},
    {"username": "user2", "datasets": ["SYNTHETIC-POG", "SYNTHETIC-BIO-CAN"]},
]


# Debug toolbar settings

if DEBUG:
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + [
        "127.0.0.1",
        "10.0.2.2",
    ]
