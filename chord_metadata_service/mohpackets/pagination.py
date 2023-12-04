from typing import Any, List, Optional

from ninja import Field, Schema
from ninja.pagination import (
    PaginationBase,
    RouterPaginated,
)

"""
    This module contains the PAGINATION classes. It is used to
    break down the long result like a list of all DONORS into pages by adding the
    pagination_class to the API view.

    User can specify the page size by adding the query parameter 'page_size' to
    the request URL.

    The default page size is 100, and the maximum page size is 1000.

    Author: Son Chau
"""

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 100


class CustomPagination(PaginationBase):
    class Input(Schema):
        page: int = Field(None, ge=1)
        page_size: int = Field(None, ge=1)

    class Output(Schema):
        items: List[Any] = []
        count: Optional[int]
        next_page: Optional[int]
        previous_page: Optional[int]

    def paginate_queryset(self, queryset, pagination: Input, **params):
        pagination.page = pagination.page or DEFAULT_PAGE
        pagination.page_size = pagination.page_size or DEFAULT_PAGE_SIZE

        offset = (pagination.page - 1) * pagination.page_size

        total_items = queryset.count()
        items = list(queryset[offset : offset + pagination.page_size])  # noqa: E203

        next_page = (
            pagination.page + 1 if offset + pagination.page_size < total_items else None
        )
        previous_page = pagination.page - 1 if pagination.page > 1 else None

        return {
            "items": items,
            "count": len(items),
            "next_page": next_page,
            "previous_page": previous_page,
        }


class CustomRouterPaginated(RouterPaginated):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.pagination_class = CustomPagination
