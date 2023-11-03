"""Jira tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_jira import streams


class TapJira(Tap):
    """Jira tap class."""

    name = "tap-jira"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "username",
            th.StringType,
            required=True,
            description="The username (email) to authenticate against the API service",
        ),
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description="The API token to authenticate against the API service",
        ),
        th.Property(
            "domain",
            th.StringType,
            required=True,
            description="The domain for the JIRA instance (e.g. 'mycompany.atlassian.net')",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
        ),
        th.Property(
            "custom_fields",
            th.ObjectType(additional_properties=th.StringType),
            description="A mapping of custom field IDs to their names",
        )
    ).to_dict()

    def discover_streams(self) -> list[streams.JiraStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.IssuesStream(self),
            streams.UsersStream(self),
            streams.BoardsStream(self),
            streams.SprintsStream(self),
            streams.WorkflowStatusesStream(self),
        ]


if __name__ == "__main__":
    TapJira.cli()
