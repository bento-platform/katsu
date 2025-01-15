import structlog

__all__ = [
    "logger",
]

logger = structlog.getLogger("katsu")
