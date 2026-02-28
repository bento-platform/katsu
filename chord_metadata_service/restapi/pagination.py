from django.conf import settings
from rest_framework import pagination
from urllib.parse import urljoin


__all__ = [
    "DEFAULT_PAGE_SIZE",
    "DEFAULT_MAX_PAGE_SIZE",
    "LargeResultsSetPagination",
    "BatchResultsSetPagination",
]


DEFAULT_PAGE_SIZE: int = 25
DEFAULT_MAX_PAGE_SIZE: int = 10000


class LargeResultsSetPagination(pagination.PageNumberPagination):
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = DEFAULT_MAX_PAGE_SIZE

    # Fix next/previous links inside sub-path-mounted reverse proxies in the Bento context:

    def _get_absolute_uri(self):
        full_path = self.request.get_full_path()
        return urljoin(f"{settings.SERVICE_URL_BASE_PATH}/", full_path.removeprefix("/"))

    def get_next_link(self):
        if settings.SERVICE_URL_BASE_PATH is not None:
            # Monkey-patch rewrite build_absolute_uri
            self.request.build_absolute_uri = self._get_absolute_uri
        return super(LargeResultsSetPagination, self).get_next_link()

    def get_previous_link(self):
        if settings.SERVICE_URL_BASE_PATH is not None:
            # Monkey-patch rewrite build_absolute_uri
            self.request.build_absolute_uri = self._get_absolute_uri
        return super(LargeResultsSetPagination, self).get_previous_link()

    def get_html_context(self):
        if settings.SERVICE_URL_BASE_PATH is not None:
            # Monkey-patch rewrite build_absolute_uri
            self.request.build_absolute_uri = self._get_absolute_uri
        super(LargeResultsSetPagination, self).get_html_context()


class BatchResultsSetPagination(LargeResultsSetPagination):
    """
    Overrides the page_size parameter with the max page size value.
    This allows for results to be formatted in a single page without having to pass
    an arbitrary page_size as a GET parameter.
    """

    def get_page_size(self, request):
        return self.max_page_size
