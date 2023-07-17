#############################################################
#                  LOCAL SETTINGS                           #
# Customize configuration specific to the local development #
# environment. Inherit from setting base.py and use:        #
# - localhost                                               #
# - debug toolbar enable                                    #
# - local postgres database                                 #
# - user1 set to authorize SYNTHETIC-1                      #
# - user2 set to authorize SYNTHETIC-1, SYNTHETIC-2         #
# - testing token is user1 and user2                        #
#############################################################

from .base import *

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

INSTALLED_APPS.append("debug_toolbar")
INSTALLED_APPS.append("drf_spectacular")

MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "drf_spectacular.openapi.AutoSchema"

# DRF Spectacular settings
# ------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "MoH Service API",
    "DESCRIPTION": ("This is the RESTful API for the MoH Service."),
    "VERSION": "1.0.0",
    # include schema endpoint into schema
    "SERVE_INCLUDE_SCHEMA": False,
    # Filter out the url patterns we don't want documented
    "PREPROCESSING_HOOKS": ["config.hooks.preprocessing_filter_path"],
    # Split components into request and response parts where appropriate
    "COMPONENT_SPLIT_REQUEST": True,
    # Aid client generator targets that have trouble with read-only properties.
    "COMPONENT_NO_READ_ONLY_REQUIRED": True,
    # Create separate components for PATCH endpoints (without required list)
    "COMPONENT_SPLIT_PATCH": True,
    # Adds "blank" and "null" enum choices where appropriate. disable on client generation issues
    "ENUM_ADD_EXPLICIT_BLANK_NULL_CHOICE": True,
    # Determines if and how free-form 'additionalProperties' should be emitted in the schema. Some
    # code generator targets are sensitive to this. None disables generic 'additionalProperties'.
    # allowed values are 'dict', 'bool', None
    "GENERIC_ADDITIONAL_PROPERTIES": "dict",
    # Determines whether operation parameters should be sorted alphanumerically or just in
    # the order they arrived. Accepts either True, False, or a callable for sort's key arg.
    "SORT_OPERATION_PARAMETERS": False,
    # modify and override the SwaggerUI template
    "SWAGGER_UI_SETTINGS": {
        "docExpansion": "none",  # collapse all endpoints by default
    },
    # Specify Enum names for choices used by multiple fields
    "ENUM_NAME_OVERRIDES": {
        "uBooleanEnum": "chord_metadata_service.mohpackets.permissible_values.UBOOLEAN",
        "TCategoryEnum": "chord_metadata_service.mohpackets.permissible_values.T_CATEGORY",
        "NCategoryEnum": "chord_metadata_service.mohpackets.permissible_values.N_CATEGORY",
        "MCategoryEnum": "chord_metadata_service.mohpackets.permissible_values.M_CATEGORY",
        "StageGroupEnum": "chord_metadata_service.mohpackets.permissible_values.STAGE_GROUP",
        "StagingSystemEnum": "chord_metadata_service.mohpackets.permissible_values.TUMOUR_STAGING_SYSTEM",
        "ReferencePathologyEnum": "chord_metadata_service.mohpackets.permissible_values.CONFIRMED_DIAGNOSIS_TUMOUR",
        "MarginTypesEnum": "chord_metadata_service.mohpackets.permissible_values.MARGIN_TYPES",
        "DosageUnitsEnum": "chord_metadata_service.mohpackets.permissible_values.DOSAGE_UNITS",
        "ErPrHpvStatusEnum": "chord_metadata_service.mohpackets.permissible_values.ER_PR_HPV_STATUS",
        "Her2StatusEnum": "chord_metadata_service.mohpackets.permissible_values.HER2_STATUS",
    },
}
# ==============================================================================
# DATABASES SETTINGS
# ==============================================================================

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

# You can change username and datasets to suit your needs
LOCAL_AUTHORIZED_DATASET = [
    {"username": "user1", "datasets": ["SYNTHETIC-1"]},
    {"username": "user2", "datasets": ["SYNTHETIC-1", "SYNTHETIC-2"]},
]

# Debug toolbar settings
# ----------------------
if DEBUG:
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + [
        "127.0.0.1",
        "10.0.2.2",
    ]
