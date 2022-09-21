from .settings import *  # noqa: F403, F401

# This allowed to run the tests without keycloak running and we cannot get the token from keycloak
# If we figure out to do the integration tests, we can remove this
CANDIG_AUTHORIZATION = ''
