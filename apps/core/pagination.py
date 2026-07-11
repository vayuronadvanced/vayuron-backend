"""
Shared pagination classes.
"""

from rest_framework.pagination import PageNumberPagination


class StandardResultsPagination(PageNumberPagination):
    """
    Default page size stays small for normal dashboard browsing, but allows
    the client to request up to 1000 per page (e.g. `?page_size=1000`) for
    CSV export (Phase 4.3), avoiding a dedicated export endpoint.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 1000
