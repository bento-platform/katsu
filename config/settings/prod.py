#####################################################################
#                   PRODUCTION SETTINGS                             #
# Inherit from setting base.py. Contain only necessary settings to  #
# make the project run. Following:                                  #
# https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/ #
#####################################################################

import os
from os.path import exists

from .base import *

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "docker.localhost",
    "candig.docker.internal",
    os.environ.get("HOST_CONTAINER_NAME"),
]

# CANDIG SETTINGS
# ---------------
KATSU_AUTHORIZATION = os.getenv("KATSU_AUTHORIZATION")
CANDIG_OPA_URL = os.getenv("OPA_URL")
CANDIG_OPA_SITE_ADMIN_KEY = os.getenv("OPA_SITE_ADMIN_KEY")
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

DEBUG = False

SECRET_KEY = os.environ.get("DJANGO_SECRET")

SECURE_HSTS_SECONDS = 3600  # Once confirm that all assets are served securely(i.e. HSTS didn’t break anything), increase this value

SECURE_SSL_REDIRECT = True

SECURE_HSTS_INCLUDE_SUBDOMAINS = True

CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True

SECURE_HSTS_PRELOAD = True
