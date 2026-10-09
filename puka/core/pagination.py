from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.core.paginator import Paginator

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest

#: Page sizes offered by the pager's size menu.
PAGE_SIZE_OPTIONS = (10, 25, 50, 100)

#: Items per page when no valid ``page_size`` query parameter is given.
DEFAULT_PAGE_SIZE = 10


class PageSizePaginator(Paginator):
    """Paginator that exposes its allowed page sizes to templates."""

    page_size_options = PAGE_SIZE_OPTIONS


class PageSizeMixin:
    """ListView: ``?page_size=`` selects the page size, defaulting to 10."""

    paginate_by: int | None = DEFAULT_PAGE_SIZE
    paginator_class = PageSizePaginator
    request: HttpRequest

    def get_paginate_by(self, queryset: QuerySet[Any]) -> int | None:  # noqa: ARG002
        try:
            page_size = int(self.request.GET.get("page_size", ""))
        except ValueError:
            return self.paginate_by
        return page_size if page_size in PAGE_SIZE_OPTIONS else self.paginate_by
