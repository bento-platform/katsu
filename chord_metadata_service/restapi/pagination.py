from django.conf import settings
from rest_framework import pagination
from rest_framework.utils.urls import remove_query_param, replace_query_param
from urllib.parse import urljoin


__all__ = [
    "LargeResultsSetPagination",
]


class LargeResultsSetPagination(pagination.PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 10000

    # Fix next/previous links inside sub-path-mounted reverse proxies in the CHORD context

    def _get_chord_absolute_uri(self):
        return urljoin(settings.CHORD_URL, self.request.get_full_path())

    def get_next_link(self):
        if not self.page.has_next():
            return None

        if settings.CHORD_URL is not None:
            url = self._get_chord_absolute_uri()
            page_number = self.page.next_page_number()
            return replace_query_param(url, self.page_query_param, page_number)

        return super(LargeResultsSetPagination, self).get_next_link()

    def get_previous_link(self):
        if not self.page.has_previous():
            return None

        if settings.CHORD_URL is not None:
            url = self._get_chord_absolute_uri()
            page_number = self.page.next_page_number()
            if page_number == 1:
                return remove_query_param(url, self.page_query_param)
            return replace_query_param(url, self.page_query_param, page_number)

        return super(LargeResultsSetPagination, self).get_previous_link()
