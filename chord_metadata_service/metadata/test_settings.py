from .settings import *  # noqa: F403, F401

# Tests are run locally with the Django dev server. Adding a sub-path which
# is managed by the gateway in production, creates wrong references and breaks
# almost every test. This resets the setting for when an environment variable
# CHORD_METADATA_SUB_PATH had been set.
FORCE_SCRIPT_NAME = ''
