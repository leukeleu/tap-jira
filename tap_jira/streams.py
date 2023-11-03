"""Stream type classes for tap-jira."""

from __future__ import annotations

import sys
import typing as t
from http import HTTPStatus
from typing import Any

import requests
from singer_sdk import typing as th  # JSON Schema typing helpers
from singer_sdk.helpers.jsonpath import extract_jsonpath

from tap_jira.client import JiraStream
from tap_jira.paginators import JiraPaginator, OffsetPaginator

USER_PROPERTY = th.ObjectType(
    th.Property("displayName", th.StringType),
    th.Property("emailAddress", th.StringType),
    th.Property("accountId", th.StringType),
    th.Property("active", th.BooleanType),
)

if t.TYPE_CHECKING:
    from singer_sdk.pagination import BaseAPIPaginator


class JiraAgileApiStream(JiraStream):
    """Base class for Jira Agile API streams."""

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return f"https://{self.config['domain']}/rest/agile/1.0"


class BoardsStream(JiraAgileApiStream):
    """Boards stream."""

    name = "boards"
    path = "/board"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None
    records_jsonpath = "$.values[*]"
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("name", th.StringType),
        th.Property("type", th.StringType),
        th.Property(
            "location",
            th.ObjectType(
                th.Property("projectId", th.IntegerType),
                th.Property("displayName", th.StringType),
                th.Property("projectName", th.StringType),
                th.Property("projectKey", th.StringType),
                th.Property("projectTypeKey", th.StringType),
                th.Property("name", th.StringType),
            ),
        ),
    ).to_dict()

    def get_child_context(self, record: dict, context: dict | None) -> dict | None:
        """Return a dictionary of values to be used in URL parameterization.

        @param record:
        @param context:
        @return:
        """
        return {"board_id": record["id"]}


class SprintsStream(JiraAgileApiStream):
    """Sprints stream."""

    parent_stream_type = BoardsStream
    name = "sprints"
    path = "/board/{board_id}/sprint"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None
    records_jsonpath = "$.values[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("name", th.StringType),
        th.Property("state", th.StringType),
        th.Property("startDate", th.DateTimeType),
        th.Property("endDate", th.DateTimeType),
        th.Property("completeDate", th.DateTimeType),
        th.Property("originBoardId", th.IntegerType),
        th.Property("goal", th.StringType),
    ).to_dict()

    def validate_response(self, response: requests.Response) -> None:
        """Validate the response from the API.

        Special-case handling for boards that do not support sprints.
        @param response:
        @return:
        """
        if response.status_code == HTTPStatus.BAD_REQUEST and response.json()[
            "errorMessages"
        ] == ["The board does not support sprints"]:
            return

        super().validate_response(response)

    def get_child_context(self, record: dict, context: dict | None) -> dict | None:
        """Return a dictionary of values to be used in URL parameterization.

        @param record:
        @param context:
        @return:
        """
        return {"sprint_id": record["id"]}


class IssuesStream(JiraAgileApiStream):
    """Issues stream."""

    parent_stream_type = BoardsStream
    name = "issues"
    path = "/board/{board_id}/issue"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "updated"
    records_jsonpath = "$.issues[*]"
    next_page_token_jsonpath = "$.startAt"  # noqa: S105

    @property
    def custom_field_mapping(self) -> dict:
        """Custom field mapping from config."""
        return self.config.get("custom_fields", {})

    @property
    def schema(self) -> dict:
        """Schema with custom fields from config."""
        issue_type = th.Property(
            "issuetype",
            th.ObjectType(
                th.Property("id", th.StringType),
                th.Property("name", th.StringType),
                th.Property("subtask", th.BooleanType),
                th.Property("hierarchyLevel", th.IntegerType),
            ),
        )
        status = th.Property(
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

        project_property = th.ObjectType(
            th.Property("id", th.StringType),
            th.Property("key", th.StringType),
            th.Property("name", th.StringType),
            th.Property("projectTypeKey", th.StringType),
        )

        return th.PropertiesList(
            th.Property("id", th.StringType),
            th.Property("key", th.StringType),
            th.Property("updated", th.DateTimeType),
            th.Property("sprint_id", th.IntegerType),
            th.Property(
                "changelog",
                th.ObjectType(
                    th.Property(
                        "histories",
                        th.ArrayType(
                            th.ObjectType(
                                th.Property("id", th.StringType),
                                th.Property("issueId", th.StringType),
                                th.Property("created", th.DateTimeType),
                                th.Property("author", USER_PROPERTY),
                                th.Property(
                                    "items",
                                    th.ArrayType(
                                        th.ObjectType(
                                            th.Property("field", th.StringType),
                                            th.Property("fieldtype", th.StringType),
                                            th.Property("from", th.StringType),
                                            th.Property("fromString", th.StringType),
                                            th.Property("to", th.StringType),
                                            th.Property("toString", th.StringType),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    )
                ),
            ),
            th.Property(
                "fields",
                th.ObjectType(
                    th.Property("summary", th.StringType),
                    th.Property("project", project_property),
                    status,
                    th.Property("assignee", USER_PROPERTY),
                    issue_type,
                    th.Property(
                        "parent",
                        th.ObjectType(
                            th.Property("id", th.StringType),
                            th.Property("key", th.StringType),
                            th.Property(
                                "fields",
                                th.ObjectType(
                                    th.Property("summary", th.StringType),
                                    issue_type,
                                    status,
                                ),
                            ),
                        ),
                    ),
                    th.Property("created", th.DateTimeType),
                    th.Property("labels", th.ArrayType(th.StringType)),
                    *[
                        th.Property(key, th.StringType)  # TODO: This is not always a string
                        for key in self.custom_field_mapping.values()
                    ]
                ),
            ),
        ).to_dict()

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
            "expand": "changelog",
            "fieldsByKeys": True,
            "fields": [
                "summary",
                "project",
                "status",
                "assignee",
                "issuetype",
                "parent",
                "sprint",
                "updated",
                "created",
                "labels",
                *self.custom_field_mapping.keys(),
            ],
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
        row["fields"].update({
            self.custom_field_mapping[key]: value
            for key, value in row["fields"].items()
            if key in self.custom_field_mapping
        })

        # Remove custom field IDs from the fields object
        for key in self.custom_field_mapping:
            row["fields"].pop(key, None)

        row["updated"] = row["fields"]["updated"]
        row["sprint_id"] = (
            row["fields"]["sprint"]["id"] if row["fields"]["sprint"] else None
        )
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


class WorkflowStatusesStream(JiraStream):
    """Workflow statuses stream.

    This is an unpaginated response
    """

    name = "workflow_statuses"
    path = "/status"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("name", th.StringType),
        th.Property("description", th.StringType),
        th.Property("statusCategory", th.PropertiesList(
            th.Property("id", th.IntegerType),
            th.Property("key", th.StringType),
            th.Property("name", th.StringType),
        )),
    ).to_dict()
