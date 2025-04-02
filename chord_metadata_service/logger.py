import structlog
from bento_lib.logging.structured.django import BentoDjangoAccessLoggerMiddleware

__all__ = [
    "logger",
]

logger: structlog.stdlib.BoundLogger = structlog.stdlib.get_logger("katsu")

access = BentoDjangoAccessLoggerMiddleware(
    access_logger=structlog.stdlib.get_logger("katsu.access"), service_logger=logger
)
access_middleware = access.make_django_middleware()
