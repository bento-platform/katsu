import os
from os.path import exists

from .base import *

DEBUG = True
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "docker.localhost",
    os.environ.get("HOST_CONTAINER_NAME"),
]

# CANDIG SETTINGS
if exists("/run/secrets/opa-root-token"):
    with open("/run/secrets/opa-root-token", "r") as f:
        CANDIG_OPA_SECRET = f.read()


# function to read docker secret password file
def get_secret(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.readline().strip()
    except (FileNotFoundError, PermissionError) as err:
        print("Error reading secret file: %s" % err)
        raise


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DATABASE"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": get_secret(os.environ.get("POSTGRES_PASSWORD_FILE")),
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": os.environ.get("POSTGRES_PORT"),
    }
}

# Debug toolbar settings
# ----------------------
if DEBUG:
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + [
        "127.0.0.1",
        "10.0.2.2",
    ]
