host_container_name = os.environ.get("HOST_CONTAINER_NAME")

from .base import *

if host_container_name:
    ALLOWED_HOSTS.append(host_container_name)
    ALLOWED_HOSTS = list(set(ALLOWED_HOSTS))

SECRET_KEY = ""
