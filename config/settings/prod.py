import os

from .dev import *

DEBUG = False

ALLOWED_HOSTS = [os.environ.get("HOST_CONTAINER_NAME")]

SECRET_KEY = ""
