from __future__ import annotations

from requests import Response
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseOffsetPaginator


class JiraPaginator(BaseOffsetPaginator):
    """Jira paginator class."""

    def get_total(self, response: Response) -> int | None:
        """Determine the total number of records from the response."""
        return next(extract_jsonpath("$.total", response.json()), None)

    def has_more(self, response: Response) -> bool:
        """Determine the next page token from the response.

        @param response:
        @return:
        """
        return self.get_total(response) > self.get_next(response)


class OffsetPaginator(BaseOffsetPaginator):
    """Offset paginator class."""

    def has_more(self, response: Response) -> bool:
        """Whether there are more records to paginate.

        @param response:
        @return:
        """
        return len(response.json()) == self._page_size

    def get_next(self, response: Response) -> int | None:
        """Get the next page token from the response.

        @param response:
        @return:
        """
        return len(response.json()) + self.current_value
