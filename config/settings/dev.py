#############################################################
#                  DEV SETTINGS                             #
# Customize configuration specific to the dev environment   #
# Inherit from setting base.py and use:                     #
# - candig.docker.internal                                  #
# - debug toolbar enable                                    #
# - docker postgres database                                #
# - user and datasets permission from OPA                   #
# - testing token obtain from keycloak                      #
#############################################################

import os
from os.path import exists

from .local import *

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "candig.docker.internal",
    os.environ.get("HOST_CONTAINER_NAME"),
]

# CANDIG SETTINGS
# ---------------
KATSU_AUTHORIZATION = os.getenv("KATSU_AUTHORIZATION")
CANDIG_OPA_URL = os.getenv("OPA_URL")
CANDIG_OPA_SITE_ADMIN_KEY = os.getenv("OPA_SITE_ADMIN_KEY")
CONN_MAX_AGE = int(os.getenv("CONN_MAX_AGE", 0))
if exists("/run/secrets/opa-root-token"):
    with open("/run/secrets/opa-root-token", "r") as f:
        CANDIG_OPA_SECRET = f.read()
if exists("/run/secrets/katsu_secret"):
    with open("/run/secrets/katsu_secret", "r") as f:
        SECRET_KEY = f.read()


# function to read docker secret password file
def get_secret(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.readline().strip()
    except (FileNotFoundError, PermissionError) as err:
        print("Error reading secret file: %s" % err)
        raise


# ==============================================================================
# DATABASES SETTINGS
# ==============================================================================

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

# Logging
# -------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "[%(asctime)s] [%(name)s] %(levelname)s: %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "file": {
            "format": "[%(asctime)s] [%(name)s] %(levelname)s: %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
            "level": "DEBUG",  # Set the log level for the console handler
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "logs.txt"),
            "formatter": "file",
            "maxBytes": 1024 * 1024,
            "backupCount": 5,
            "level": "DEBUG",  # Set the log level for the file handler
        },
    },
    "loggers": {
        "": {
            "level": "DEBUG",  # Set the root logger level
            "handlers": ["console", "file"],
        },
        "psycopg": {
            "level": "ERROR",
        },
        "factory": {
            "level": "ERROR",
        },
        "faker": {
            "level": "ERROR",
        },
    },
}
