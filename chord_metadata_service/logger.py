import structlog

__all__ = [
    "logger",
]

logger: structlog.stdlib.BoundLogger = structlog.stdlib.get_logger("katsu")
