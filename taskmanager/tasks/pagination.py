from ninja.pagination import PaginationBase
from ninja import Schema


class CustomTaskManagerPagination(PaginationBase):
    class Input(Schema):
        """
        Defines the input schema for pagination.
        The client specifies the number of records to skip using `skip_records`.
        """

        skip_records: int = 0  # Default to 0 if not provided

    class Output(Schema):
        """
        Defines the output schema for pagination.
        Includes:
        - `items`: The paginated items.
        - `count`: Total number of items in the queryset.
        - `page_size`: Number of items per page.
        """

        items: list  # The paginated data
        count: int  # Total count of records
        page_size: int  # Number of items per page

    def paginate_queryset(self, queryset, pagination, **params):
        """
        Paginates the queryset based on the `skip_records` parameter.
        """
        skip_records = pagination.skip_records
        page_size = 5  # Fixed page size
        paginated_data = queryset[skip_records : skip_records + page_size]

        return {
            "items": paginated_data,
            "count": queryset.count(),
            "page_size": page_size,
        }
