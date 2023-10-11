"""Tests standard tap features using the built-in SDK tests library."""

import datetime
import re

from singer_sdk.testing.legacy import get_standard_tap_tests

from tap_jira.tap import TapJira

SAMPLE_CONFIG = {
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
    "username": "test@example.org",
    "api_key": "test",
    "domain": "test.atlassian.net",
}

SEARCH_RESPONSE = {
    "expand": "names,schema",
    "startAt": 0,
    "maxResults": 50,
    "total": 1,
    "issues": [
        {
            "expand": "",
            "id": "10002",
            "self": "https://your-domain.atlassian.net/rest/api/3/issue/10002",
            "key": "ED-1",
            "fields": {
                "watcher": {
                    "self": "https://your-domain.atlassian.net/rest/api/3/issue/EX-1/watchers",
                    "isWatching": False,
                    "watchCount": 1,
                    "watchers": [
                        {
                            "self": "https://your-domain.atlassian.net/rest/api/3/user?accountId=5b10a2844c20165700ede21g",
                            "accountId": "5b10a2844c20165700ede21g",
                            "displayName": "Mia Krystof",
                            "active": False,
                        }
                    ],
                },
                "attachment": [
                    {
                        "id": 10000,
                        "self": "https://your-domain.atlassian.net/rest/api/3/attachments/10000",
                        "filename": "picture.jpg",
                        "author": {
                            "self": "https://your-domain.atlassian.net/rest/api/3/user?accountId=5b10a2844c20165700ede21g",
                            "key": "",
                            "accountId": "5b10a2844c20165700ede21g",
                            "accountType": "atlassian",
                            "name": "",
                            "avatarUrls": {
                                "48x48": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=48&s=48",
                                "24x24": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=24&s=24",
                                "16x16": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=16&s=16",
                                "32x32": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=32&s=32",
                            },
                            "displayName": "Mia Krystof",
                            "active": False,
                        },
                        "created": "2023-10-09T09:29:19.289+0000",
                        "size": 23123,
                        "mimeType": "image/jpeg",
                        "content": "https://your-domain.atlassian.net/jira/rest/api/3/attachment/content/10000",
                        "thumbnail": "https://your-domain.atlassian.net/jira/rest/api/3/attachment/thumbnail/10000",
                    }
                ],
                "sub-tasks": [
                    {
                        "id": "10000",
                        "type": {
                            "id": "10000",
                            "name": "",
                            "inward": "Parent",
                            "outward": "Sub-task",
                        },
                        "outwardIssue": {
                            "id": "10003",
                            "key": "ED-2",
                            "self": "https://your-domain.atlassian.net/rest/api/3/issue/ED-2",
                            "fields": {
                                "status": {
                                    "iconUrl": "https://your-domain.atlassian.net/images/icons/statuses/open.png",
                                    "name": "Open",
                                }
                            },
                        },
                    }
                ],
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": "Main order flow broken"}
                            ],
                        }
                    ],
                },
                "project": {
                    "self": "https://your-domain.atlassian.net/rest/api/3/project/EX",
                    "id": "10000",
                    "key": "EX",
                    "name": "Example",
                    "avatarUrls": {
                        "48x48": "https://your-domain.atlassian.net/secure/projectavatar?size=large&pid=10000",
                        "24x24": "https://your-domain.atlassian.net/secure/projectavatar?size=small&pid=10000",
                        "16x16": "https://your-domain.atlassian.net/secure/projectavatar?size=xsmall&pid=10000",
                        "32x32": "https://your-domain.atlassian.net/secure/projectavatar?size=medium&pid=10000",
                    },
                    "projectCategory": {
                        "self": "https://your-domain.atlassian.net/rest/api/3/projectCategory/10000",
                        "id": "10000",
                        "name": "FIRST",
                        "description": "First Project Category",
                    },
                    "simplified": False,
                    "style": "classic",
                    "insight": {
                        "totalIssueCount": 100,
                        "lastIssueUpdateTime": "2023-10-09T09:29:19.287+0000",
                    },
                },
                "comment": [
                    {
                        "self": "https://your-domain.atlassian.net/rest/api/3/issue/10010/comment/10000",
                        "id": "10000",
                        "author": {
                            "self": "https://your-domain.atlassian.net/rest/api/3/user?accountId=5b10a2844c20165700ede21g",
                            "accountId": "5b10a2844c20165700ede21g",
                            "displayName": "Mia Krystof",
                            "active": False,
                        },
                        "body": {
                            "type": "doc",
                            "version": 1,
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque eget venenatis elit. Duis eu justo eget augue iaculis fermentum. Sed semper quam laoreet nisi egestas at posuere augue semper.",
                                        }
                                    ],
                                }
                            ],
                        },
                        "updateAuthor": {
                            "self": "https://your-domain.atlassian.net/rest/api/3/user?accountId=5b10a2844c20165700ede21g",
                            "accountId": "5b10a2844c20165700ede21g",
                            "displayName": "Mia Krystof",
                            "active": False,
                        },
                        "created": "2021-01-17T12:34:00.000+0000",
                        "updated": "2021-01-18T23:45:00.000+0000",
                        "visibility": {
                            "type": "role",
                            "value": "Administrators",
                            "identifier": "Administrators",
                        },
                    }
                ],
                "issuelinks": [
                    {
                        "id": "10001",
                        "type": {
                            "id": "10000",
                            "name": "Dependent",
                            "inward": "depends on",
                            "outward": "is depended by",
                        },
                        "outwardIssue": {
                            "id": "10004L",
                            "key": "PR-2",
                            "self": "https://your-domain.atlassian.net/rest/api/3/issue/PR-2",
                            "fields": {
                                "status": {
                                    "iconUrl": "https://your-domain.atlassian.net/images/icons/statuses/open.png",
                                    "name": "Open",
                                }
                            },
                        },
                    },
                    {
                        "id": "10002",
                        "type": {
                            "id": "10000",
                            "name": "Dependent",
                            "inward": "depends on",
                            "outward": "is depended by",
                        },
                        "inwardIssue": {
                            "id": "10004",
                            "key": "PR-3",
                            "self": "https://your-domain.atlassian.net/rest/api/3/issue/PR-3",
                            "fields": {
                                "status": {
                                    "iconUrl": "https://your-domain.atlassian.net/images/icons/statuses/open.png",
                                    "name": "Open",
                                }
                            },
                        },
                    },
                ],
                "worklog": [
                    {
                        "self": "https://your-domain.atlassian.net/rest/api/3/issue/10010/worklog/10000",
                        "author": {
                            "self": "https://your-domain.atlassian.net/rest/api/3/user?accountId=5b10a2844c20165700ede21g",
                            "accountId": "5b10a2844c20165700ede21g",
                            "displayName": "Mia Krystof",
                            "active": False,
                        },
                        "updateAuthor": {
                            "self": "https://your-domain.atlassian.net/rest/api/3/user?accountId=5b10a2844c20165700ede21g",
                            "accountId": "5b10a2844c20165700ede21g",
                            "displayName": "Mia Krystof",
                            "active": False,
                        },
                        "comment": {
                            "type": "doc",
                            "version": 1,
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "I did some work here.",
                                        }
                                    ],
                                }
                            ],
                        },
                        "updated": "2021-01-18T23:45:00.000+0000",
                        "visibility": {
                            "type": "group",
                            "value": "jira-developers",
                            "identifier": "276f955c-63d7-42c8-9520-92d01dca0625",
                        },
                        "started": "2021-01-17T12:34:00.000+0000",
                        "timeSpent": "3h 20m",
                        "timeSpentSeconds": 12000,
                        "id": "100028",
                        "issueId": "10002",
                    }
                ],
                "updated": "2021-01-19T23:45:00.000+0000",
                "timetracking": {
                    "originalEstimate": "10m",
                    "remainingEstimate": "3m",
                    "timeSpent": "6m",
                    "originalEstimateSeconds": 600,
                    "remainingEstimateSeconds": 200,
                    "timeSpentSeconds": 400,
                },
            },
        }
    ],
    "warningMessages": ["The value 'bar' does not exist for the field 'foo'."],
}

ISSUE_HISTORY_RESPONSE = {
    "self": "https://your-domain.atlassian.net/rest/api/3/issue/TT-1/changelog?startAt=2&maxResults=2",
    "nextPage": "https://your-domain.atlassian.net/rest/api/3/issue/TT-1/changelog?&startAt=4&maxResults=2",
    "maxResults": 2,
    "startAt": 2,
    "total": 5,
    "isLast": False,
    "values": [
        {
            "id": "10001",
            "author": {
                "self": "https://your-domain.atlassian.net/rest/api/3/user?accountId=5b10a2844c20165700ede21g",
                "accountId": "5b10a2844c20165700ede21g",
                "emailAddress": "mia@example.com",
                "avatarUrls": {
                    "48x48": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=48&s=48",
                    "24x24": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=24&s=24",
                    "16x16": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=16&s=16",
                    "32x32": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=32&s=32",
                },
                "displayName": "Mia Krystof",
                "active": True,
                "timeZone": "Australia/Sydney",
            },
            "created": "1970-01-18T06:27:50.429+0000",
            "items": [
                {
                    "field": "fields",
                    "fieldtype": "jira",
                    "fieldId": "fieldId",
                    "from": None,
                    "fromString": "",
                    "to": None,
                    "toString": "label-1",
                }
            ],
        },
        {
            "id": "10002",
            "author": {
                "self": "https://your-domain.atlassian.net/rest/api/3/user?accountId=5b10a2844c20165700ede21g",
                "accountId": "5b10a2844c20165700ede21g",
                "emailAddress": "mia@example.com",
                "avatarUrls": {
                    "48x48": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=48&s=48",
                    "24x24": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=24&s=24",
                    "16x16": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=16&s=16",
                    "32x32": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=32&s=32",
                },
                "displayName": "Mia Krystof",
                "active": True,
                "timeZone": "Australia/Sydney",
            },
            "created": "1970-01-18T06:27:51.429+0000",
            "items": [
                {
                    "field": "fields",
                    "fieldtype": "jira",
                    "fieldId": "fieldId",
                    "from": None,
                    "fromString": "label-1",
                    "to": None,
                    "toString": "label-1 label-2",
                }
            ],
        },
    ],
}

USERS_RESPONSE = [
  {
    "self": "https://your-domain.atlassian.net/rest/api/3/user?accountId=5b10a2844c20165700ede21g",
    "key": "",
    "accountId": "5b10a2844c20165700ede21g",
    "accountType": "atlassian",
    "name": "",
    "avatarUrls": {
      "48x48": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=48&s=48",
      "24x24": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=24&s=24",
      "16x16": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=16&s=16",
      "32x32": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=32&s=32"
    },
    "displayName": "Mia Krystof",
    "active": False
  },
  {
    "self": "https://your-domain.atlassian.net/rest/api/3/user?accountId=5b10ac8d82e05b22cc7d4ef5",
    "key": "",
    "accountId": "5b10ac8d82e05b22cc7d4ef5",
    "accountType": "atlassian",
    "name": "",
    "avatarUrls": {
      "48x48": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/AA-3.png?size=48&s=48",
      "24x24": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/AA-3.png?size=24&s=24",
      "16x16": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/AA-3.png?size=16&s=16",
      "32x32": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/AA-3.png?size=32&s=32"
    },
    "displayName": "Emma Richards",
    "active": True
  }
]


# Run standard built-in tap tests from the SDK:
def test_standard_tap_tests(requests_mock) -> None:  # noqa: ANN001
    """Run standard built-in tap tests from the SDK."""
    requests_mock.get("/rest/api/3/search", json=SEARCH_RESPONSE)
    requests_mock.get(
        re.compile(r"/rest/api/3/issue/[\w-]+/changelog(\?.*)?"), json=SEARCH_RESPONSE
    )
    requests_mock.get("/rest/api/3/users", json=USERS_RESPONSE)
    tests = get_standard_tap_tests(TapJira, config=SAMPLE_CONFIG)
    for test in tests:
        test()
