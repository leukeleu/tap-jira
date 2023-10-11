"""Stream type classes for tap-jira."""

from __future__ import annotations

import typing as t
from typing import Any

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_jira.client import JiraStream
from tap_jira.paginators import JiraPaginator, OffsetPaginator

USER_TYPE = th.ObjectType(
    th.Property("displayName", th.StringType),
    th.Property("emailAddress", th.StringType),
    th.Property("accountId", th.StringType),
    th.Property("active", th.BooleanType),
)

if t.TYPE_CHECKING:
    from singer_sdk.pagination import BaseAPIPaginator


class IssuesStream(JiraStream):
    """Issues stream."""

    name = "issues"
    path = "/search"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "updated"
    records_jsonpath = "$.issues[*]"
    next_page_token_jsonpath = "$.startAt"  # noqa: S105

    ISSUE_TYPE = th.Property(
        "issuetype",
        th.ObjectType(
            th.Property("id", th.StringType),
            th.Property("name", th.StringType),
            th.Property("subtask", th.BooleanType),
            th.Property("hierarchyLevel", th.IntegerType),
        ),
    )
    STATUS = th.Property(
        "status",
        th.ObjectType(
            th.Property("id", th.StringType),
            th.Property("name", th.StringType),
            th.Property(
                "statusCategory",
                th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("key", th.StringType),
                    th.Property("name", th.StringType),
                ),
            ),
        ),
    )

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("key", th.StringType),
        th.Property("updated", th.DateTimeType),
        th.Property(
            "fields",
            th.ObjectType(
                th.Property("summary", th.StringType),
                STATUS,
                th.Property(
                    "assignee",
                    USER_TYPE,
                ),
                ISSUE_TYPE,
                th.Property(
                    "parent",
                    th.ObjectType(
                        th.Property("id", th.StringType),
                        th.Property("key", th.StringType),
                        th.Property(
                            "fields",
                            th.ObjectType(
                                th.Property("summary", th.StringType),
                                ISSUE_TYPE,
                                STATUS,
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ).to_dict()

    def get_child_context(self, record: dict, context: dict | None) -> dict | None:
        """Return a dictionary of values to be used in URL parameterization.

        @param record:
        @param context:
        @return:
        """
        return {"issue_id": record["id"]}

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,  # noqa: ANN401
    ) -> dict | None:
        """Return a JSON payload object for a request.

        Args:
            context: The context dictionary.
            next_page_token: The next page token.

        Returns:
            A dictionary of JSON payload parameters.
        """
        params = super().get_url_params(context, next_page_token)

        clauses = []

        starting_date = self.get_starting_timestamp(context)
        if starting_date:
            clauses.append(f"updated >= '{starting_date.strftime('%Y-%m-%d %H:%M')}'")

        if order_by_field := params.pop("order_by", None):
            clauses.append(
                f"ORDER BY {order_by_field} {params.pop('sort', 'ASC').upper()}"
            )

        return {
            **params,
            "jql": " ".join(clauses),
            "fields": [
                "id",
                "key",
                "updated",
                "summary",
                "status",
                "assignee",
                "issuetype",
                "parent",
            ],
            "fieldsByKeys": True,
            "validateQuery": "strict",
        }

    def post_process(
        self,
        row: dict,
        context: dict | None = None,  # noqa: ARG002
    ) -> dict | None:
        """As needed, append or transform raw data to match expected structure.

        Args:
            row: An individual record from the stream.
            context: The stream context.

        Returns:
            The updated record dictionary, or ``None`` to skip the record.
        """
        row["updated"] = row["fields"]["updated"]
        return row

    def get_new_paginator(self) -> BaseAPIPaginator:
        """Create a new pagination helper instance.

        Returns:
            A pagination helper instance.
        """
        return JiraPaginator(start_value=0, page_size=self._page_size)


class UsersStream(JiraStream):
    """Define custom stream."""

    name = "users"
    path = "/users"
    primary_keys: t.ClassVar[list[str]] = ["accountId"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property("accountId", th.StringType),
        th.Property("accountType", th.StringType),
        th.Property("displayName", th.StringType),
        th.Property("active", th.BooleanType),
        th.Property("emailAddress", th.StringType),
    ).to_dict()

    def get_new_paginator(self) -> BaseAPIPaginator:
        """Create a new pagination helper instance.

        Returns:
            A pagination helper instance.
        """
        return OffsetPaginator(start_value=0, page_size=self._page_size)


class IssueHistoryStream(JiraStream):
    """Issue history stream."""

    parent_stream_type = IssuesStream
    name = "issue_history"
    path = "/issue/{issue_id}/changelog"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "created"
    records_jsonpath = "$.values[*]"

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("issueId", th.StringType),
        th.Property("created", th.DateTimeType),
        th.Property("author", USER_TYPE),
        th.Property("items", th.ArrayType(
            th.ObjectType(
                th.Property("field", th.StringType),
                th.Property("fieldtype", th.StringType),
                th.Property("from", th.StringType),
                th.Property("fromString", th.StringType),
                th.Property("to", th.StringType),
                th.Property("toString", th.StringType),
            ),
        ))
    ).to_dict()

    def get_new_paginator(self) -> BaseAPIPaginator:
        """Create a new pagination helper instance.

        @return:
        """
        return JiraPaginator(start_value=0, page_size=self._page_size)

    def post_process(
        self,
        row: dict,
        context: dict | None = None,  # noqa: ARG002
    ) -> dict | None:
        return {
            **row,
            "issueId": context["issue_id"],
        }
