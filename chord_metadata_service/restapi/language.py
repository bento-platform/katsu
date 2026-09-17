from rest_framework.request import Request as DrfRequest

__all__ = ["get_preferred_language"]


def get_preferred_language(request: DrfRequest) -> str:
    """Normalize the primary language tag from the Accept-Language header."""
    header = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
    if not header:
        return "en"
    primary = header.split(",")[0].split(";")[0].strip()
    return primary.split("-")[0].lower() or "en"
