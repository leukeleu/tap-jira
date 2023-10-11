"""REST client handling, including JiraStream base class."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Iterable

import requests
from singer_sdk.authenticators import BasicAuthenticator

from singer_sdk.streams import RESTStream

_Auth = Callable[[requests.PreparedRequest], requests.PreparedRequest]
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class JiraStream(RESTStream):
    """Jira stream class."""

    _page_size = 100

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return f"https://{self.config['domain']}/rest/api/3"

    records_jsonpath = "$[*]"  # Or override `parse_response`.

    # Set this value or override `get_new_paginator`.
    next_page_token_jsonpath = "$.next_page"  # noqa: S105

    @property
    def authenticator(self) -> BasicAuthenticator:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        return BasicAuthenticator.create_for_stream(
            self,
            username=self.config.get("username", ""),
            password=self.config.get("api_key", ""),
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        # If not using an authenticator, you may also provide inline auth headers:
        # headers["Private-Token"] = self.config.get("auth_token")  # noqa: ERA001
        return headers

    def get_url_params(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: Any | None,  # noqa: ANN401
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["startAt"] = next_page_token
        params["maxResults"] = self._page_size
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key
        return params
