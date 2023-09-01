from rest_framework.pagination import PageNumberPagination

"""
    This module contains the PAGINATION classes. It is used to
    break down the long result like a list of all DONORS into pages by adding the
    pagination_class to the API view.

    User can specify the page size by adding the query parameter 'page_size' to
    the request URL.

    The default page size is 100, and the maximum page size is 1000.

"""


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


class SmallResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000
