"""
Django settings for metadata project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import sys
import logging
import json
from os.path import exists

from bento_lib.service_info.types import GA4GHServiceType
from urllib.parse import quote, urlparse
from dotenv import load_dotenv

from .. import __version__

load_dotenv()

logging.getLogger().setLevel(logging.INFO)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SERVICE_SECRET_KEY", '=p1@hhp5m4v0$c#eba3a+rx!$9-xk^q*7cb9(cd!wn1&_*osyc')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get(
    "KATSU_DEBUG",
    os.environ.get("BENTO_DEBUG", os.environ.get("CHORD_DEBUG", "true"))
).lower() == "true"
logging.info(f"DEBUG: {DEBUG}")

LOG_LEVEL = os.environ.get("KATSU_LOG_LEVEL", "DEBUG" if DEBUG else "INFO").upper()


# Bento-specific settings

# SECURITY WARNING: Don't run with AUTHZ_ENABLED turned off in production,
# unless an alternative permissions system is in place.
#  - This needs to be here to avoid a circular import with settings.py
BENTO_AUTHZ_ENABLED: bool = os.environ.get("BENTO_AUTHZ_ENABLED", "true").strip().lower() == "true"

BENTO_AUTHZ_SERVICE_URL: str = (
    os.environ.get("BENTO_AUTHZ_SERVICE_URL", "").strip().rstrip("/") if BENTO_AUTHZ_ENABLED else ""
)

BENTO_CONTAINER_LOCAL = os.environ.get("BENTO_CONTAINER_LOCAL", "false").lower() == "true"

CHORD_URL = os.environ.get("CHORD_URL")  # Leave None if not specified, for running in other contexts

CHORD_SERVICE_ARTIFACT = "metadata"
# NOTE: LEAVE CHORD UNLESS YOU WANT A BUNCH OF BROKEN TABLES... vvv
CHORD_SERVICE_TYPE_NO_VER = f"ca.c3g.chord:{CHORD_SERVICE_ARTIFACT}"
# ^^^
CHORD_SERVICE_TYPE: GA4GHServiceType = {
    "group": "ca.c3g.chord",
    "artifact": CHORD_SERVICE_ARTIFACT,
    "version": __version__,
}
CHORD_SERVICE_ID = os.environ.get("SERVICE_ID", CHORD_SERVICE_TYPE_NO_VER)
BENTO_SERVICE_KIND = "metadata"

# When Katsu is hosted on a subpath (e.g. http://myportal.com/api/katsu), this
# parameter is used by Django to compute correct URLs in templates (for example
# in DRF API discovery pages, or swagger UI)
FORCE_SCRIPT_NAME = os.getenv("CHORD_METADATA_SUB_PATH", "")

# Human-readable label for phenopacket data type
KATSU_PHENOPACKET_LABEL = os.getenv("KATSU_PHENOPACKET_LABEL", "Clinical Data")

# Additional allowed hosts, comma-delimited (no spaces!)
# Use HOST_CONTAINER_NAME as a separate value for backwards compatibility.
ADDITIONAL_ALLOWED_HOSTS = [
    v for v in os.environ.get("KATSU_ALLOWED_HOSTS", "").split(",")
    if v.strip()
]
if container_name := os.environ.get("HOST_CONTAINER_NAME", "").strip():
    ADDITIONAL_ALLOWED_HOSTS.append(container_name)

CHORD_HOST = urlparse(CHORD_URL or "").netloc
logging.info(f"CHORD_HOST: {CHORD_HOST}")

ALLOWED_HOSTS = [CHORD_HOST or "localhost"]
if DEBUG:
    ALLOWED_HOSTS = list(set(ALLOWED_HOSTS + ["localhost", "127.0.0.1", "[::1]"]))
if ADDITIONAL_ALLOWED_HOSTS:
    ALLOWED_HOSTS = list(set(ALLOWED_HOSTS + ADDITIONAL_ALLOWED_HOSTS))
if "*" in ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"]  # Simplify

logging.info(f"Allowed hosts: {ALLOWED_HOSTS}")

APPEND_SLASH = False

# Bento misc. settings

SERVICE_TEMP = os.environ.get("KATSU_TEMP", os.environ.get("SERVICE_TEMP"))

#  - DRS URL - by default in Bento Singularity context, use internal NGINX DRS (to avoid auth hassles)
NGINX_INTERNAL_SOCKET = quote(os.environ.get("NGINX_INTERNAL_SOCKET", "/chord/tmp/nginx_internal.sock"), safe="")
DRS_URL = os.environ.get("DRS_URL", f"http+unix://{NGINX_INTERNAL_SOCKET}/api/drs").strip().rstrip("/")

# Candig-specific settings

CANDIG_AUTHORIZATION = os.getenv("CANDIG_AUTHORIZATION", "")
CANDIG_OPA_URL = os.getenv("CANDIG_OPA_URL", "")
CANDIG_OPA_SECRET = os.getenv("CANDIG_OPA_SECRET", "my-secret-beacon-token")
CANDIG_OPA_SITE_ADMIN_KEY = os.getenv("CANDIG_OPA_SITE_ADMIN_KEY", "site-admin")
if exists("/run/secrets/opa-root-token"):
    with open("/run/secrets/opa-root-token", "r") as f:
        CANDIG_OPA_SECRET = f.read()

# Application definition

INSTALLED_APPS = (['daphne'] if os.environ.get("KATSU_CONTAINER_LOCAL") else []) + [
    'dal',
    'dal_select2',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    'chord_metadata_service.chord.apps.ChordConfig',
    'chord_metadata_service.experiments.apps.ExperimentsConfig',
    'chord_metadata_service.patients.apps.PatientsConfig',
    'chord_metadata_service.phenopackets.apps.PhenopacketsConfig',
    'chord_metadata_service.resources.apps.ResourcesConfig',
    'chord_metadata_service.restapi.apps.RestapiConfig',

    'corsheaders',
    'django_filters',
    'rest_framework',
    'adrf',
    'drf_spectacular',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'chord_metadata_service.authz.middleware.AuthzMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# This middlewares are specific to the CANDIG service
if os.getenv('INSIDE_CANDIG', ''):
    MIDDLEWARE.append('chord_metadata_service.restapi.preflight_req_middleware.PreflightRequestMiddleware')
    MIDDLEWARE.append('chord_metadata_service.restapi.candig_authz_middleware.CandigAuthzMiddleware')

CORS_ALLOWED_ORIGINS = []

CORS_PREFLIGHT_MAX_AGE = 0

ROOT_URLCONF = 'chord_metadata_service.metadata.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ASGI_APPLICATION = 'chord_metadata_service.metadata.asgi.application'
WSGI_APPLICATION = 'chord_metadata_service.metadata.wsgi.application'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'loggers': {
        '': {
            'level': LOG_LEVEL,
            'handlers': ['console'],
        },
    },
}

# if we are running the test suite, only log CRITICAL messages
if len(sys.argv) > 1 and sys.argv[1] == 'test':
    logging.disable(logging.CRITICAL)


# function to read postgres password file
def get_secret(path):
    try:
        with open(path) as sf:
            return sf.readline().strip()
    except BaseException as err:
        logging.error(f"Unexpected {err}, {type(err)}")
        raise


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }


DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.postgresql",
        'NAME': os.environ.get("POSTGRES_DATABASE", "metadata"),
        'USER': os.environ.get("POSTGRES_USER", "admin"),
        'PASSWORD': (
            get_secret(os.environ["POSTGRES_PASSWORD_FILE"])
            if os.environ.get("POSTGRES_PASSWORD_FILE")
            else os.environ.get("POSTGRES_PASSWORD", "admin")
        ),
        # Use sockets if we're inside a CHORD container / as a priority
        'HOST': os.environ.get("POSTGRES_SOCKET_DIR", os.environ.get("POSTGRES_HOST", "localhost")),
        'PORT': os.environ.get("POSTGRES_PORT", "5432"),
    }
}

# Django default cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

FHIR_INDEX_NAME = 'fhir_metadata'

# Set to True to run ES for FHIR index
ELASTICSEARCH = False

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PARSER_CLASSES': (
        # allows serializers to use snake_case field names, but parse incoming data as camelCase
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
        'djangorestframework_camel_case.parser.CamelCaseFormParser',
        'djangorestframework_camel_case.parser.CamelCaseMultiPartParser',
    ),
    # Allow any by default for DRF auth (BentoDeferToHandler is just a wrapper for doing nothing, basically)
    #  - the Bento authorization middleware will take care of denying.
    'DEFAULT_PERMISSION_CLASSES': ['chord_metadata_service.authz.permissions.BentoDeferToHandler'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'JSON_UNDERSCOREIZE': {
        'no_underscore_before_number': True
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


AUTHENTICATION_BACKENDS = (['django.contrib.auth.backends.ModelBackend'] if DEBUG else [])

# Models
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

# Cache time constant
CACHE_TIME = int(os.getenv('CACHE_TIME', 60 * 60 * 2))

# Settings related to the Public APIs

# Read project specific config.json that contains custom search fields
#  - This should not be used directly by endpoints etc. Instead, it should be accessed via the getter in restapi.utils
if os.path.isfile(os.path.join(BASE_DIR, 'config.json')):
    with open(os.path.join(BASE_DIR, 'config.json')) as config_file:
        CONFIG_PUBLIC = json.load(config_file)
else:
    CONFIG_PUBLIC = {}

# The below DISCOVERY_* settings should be accessed via the get_discovery_rules_and_field_set_permissions getter in
# API views, to correctly incorporate permissions.

# Maximum query parameters - can be sourced from environment variable; fallback to CONFIG_PUBLIC
# and if that is not set, then use 0 (no query parameters allowed)
# NOTE: This value only applies to tokens with the project-level counts permission.
#  - If this permission is not present, the effective value is 0.
#  - If the query:data permission is present, the effective value is maxsize.
DISCOVERY_MAX_QUERY_PARAMETERS = int(os.environ.get(
    "DISCOVERY_MAX_QUERY_PARAMETERS",
    CONFIG_PUBLIC.get("rules", {}).get("max_query_parameters", 0)))

# Return count threshold for censored discovery - can be sourced from environment variable; fallback to CONFIG_PUBLIC
# and if that is not set, then use sys.maxsize (effectively, everything becomes 0)
# NOTE: This value only applies to tokens with the project-level counts permission.
#  - If this permission is not present, the effective value is maxsize.
#  - If the query:data permission is present, the effective value is 0.
DISCOVERY_COUNT_THRESHOLD = int(os.environ.get(
    "DISCOVERY_COUNT_THRESHOLD",
    CONFIG_PUBLIC.get("rules", {}).get("count_threshold", sys.maxsize)))

# Public response when there is no enough data that passes the project-custom threshold
INSUFFICIENT_DATA_AVAILABLE = {"message": "Insufficient data available."}

# Public response when there is no public data available and config file is not provided
NO_PUBLIC_DATA_AVAILABLE = {"message": "No public data available."}

# Public response when public fields are not configured and config file is not provided
NO_PUBLIC_FIELDS_CONFIGURED = {"message": "No public fields configured."}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Metadata Service API',
    'DESCRIPTION': ('Metadata Service provides a phenotypic description of an '
                    'Individual in the context of biomedical research.'),
    'VERSION': __version__,
    'SERVE_INCLUDE_SCHEMA': False,
    # Filter out the url patterns we don't want documented
    'PREPROCESSING_HOOKS': ['chord_metadata_service.metadata.hooks.preprocessing_filter_path'],
    # Split components into request and response parts where appropriate
    'COMPONENT_SPLIT_REQUEST': True,
    # Aid client generator targets that have trouble with read-only properties.
    'COMPONENT_NO_READ_ONLY_REQUIRED': True,
    # Create separate components for PATCH endpoints (without required list)
    'COMPONENT_SPLIT_PATCH': True,
    # Adds "blank" and "null" enum choices where appropriate. disable on client generation issues
    'ENUM_ADD_EXPLICIT_BLANK_NULL_CHOICE': True,
    # Determines if and how free-form 'additionalProperties' should be emitted in the schema. Some
    # code generator targets are sensitive to this. None disables generic 'additionalProperties'.
    # allowed values are 'dict', 'bool', None
    'GENERIC_ADDITIONAL_PROPERTIES': 'dict',
    # Determines whether operation parameters should be sorted alphanumerically or just in
    # the order they arrived. Accepts either True, False, or a callable for sort's key arg.
    'SORT_OPERATION_PARAMETERS': False,
    # modify and override the SwaggerUI template
    'SWAGGER_UI_SETTINGS': {
        'docExpansion': 'none',  # collapse all endpoints by default
        'supportedSubmitMethods': ['get', 'put', 'post', 'delete', 'patch'] if DEBUG else ['get'],  # readonly in prod
    }
}

# SPECTACULAR_SETTINGS['SERVERS'] defines the url to which calls are made when
# testing a request within the swagger UI
if CHORD_URL:
    SPECTACULAR_SETTINGS['SERVERS'] = [{'url': CHORD_URL + FORCE_SCRIPT_NAME}]
