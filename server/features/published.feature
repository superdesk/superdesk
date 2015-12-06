Feature: Published Items Repo

    @auth
    Scenario: List empty published
        Given empty "published"
        When we get "/published"
        Then we get list with 0 items

    @auth
    Scenario: Get archive items with published state
        Given "published"
        """
        [{"_id": "tag:example.com,0000:newsml_BRE9A605", "state": "published"}]
        """
        When we get "/published"
        Then we get existing resource
        """
        {"_items": [{"_id": "tag:example.com,0000:newsml_BRE9A605", "state": "published"}]}
        """
    @auth
    Scenario: Get archive items with non-published state
        Given "published"
        """
        [{"_id": "tag:example.com,0000:newsml_BRE9A607", "state": "draft"}]
        """
        When we get "/published"
        Then we get list with 0 items

    @auth
    Scenario: Delete Item from archived
        Given "desks"
        """
        [{"name": "Sports", "content_expiry": 60}]
        """
        And "validators"
        """
        [
            {
                "schema": {},
                "type": "text",
                "act": "publish",
                "_id": "publish_text"
            }

        ]
        """
        When we post to "/subscribers" with "wire" and success
        """
        {
          "name":"Channel 1","media_type":"media", "subscriber_type": "wire", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
          "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
        }
        """
        And we post to "/archive" with success
        """
        [{"guid": "tag:example.com,0000:newsml_BRE9A605", "type": "text", "headline": "test",
          "state": "fetched", "slugline": "slugline",
          "anpa_category" : [{"qcode" : "e", "name" : "Entertainment"}],
          "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "body_html": "Test Document body"}]
        """
        When we publish "tag:example.com,0000:newsml_BRE9A605" with "publish" type and "published" state
        Then we get OK response
        When we get "/published/tag:example.com,0000:newsml_BRE9A605"
        Then we get OK response
        When we patch "/users/#CONTEXT_USER_ID#"
        """
        {"user_type": "user", "privileges": {"archived": 1, "archive": 1, "unlock": 1, "tasks": 1, "users": 1}}
        """
        Then we get OK response
        When we expire items
        """
        ["tag:example.com,0000:newsml_BRE9A605"]
        """
        When we get "/archived"
        Then we get list with 1 items
        When we delete "/archived/tag:example.com,0000:newsml_BRE9A605:2"
        Then we get response code 204
        When we get "/archived"
        Then we get list with 0 items

    @auth
    Scenario: Fails to delete from archived with no privilege
        Given "desks"
        """
        [{"name": "Sports", "content_expiry": 60}]
        """
        And "validators"
        """
        [
            {
                "schema": {},
                "type": "text",
                "act": "publish",
                "_id": "publish_text"
            }

        ]
        """
        When we post to "/subscribers" with "wire" and success
        """
        {
          "name":"Channel 1","media_type":"media", "subscriber_type": "wire", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
          "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
        }
        """
        And we post to "/archive" with success
        """
        [{"guid": "tag:example.com,0000:newsml_BRE9A605", "type": "text", "headline": "test",
          "state": "fetched", "slugline": "slugline",
          "anpa_category" : [{"qcode" : "e", "name" : "Entertainment"}],
          "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "body_html": "Test Document body"}]
        """
        When we publish "tag:example.com,0000:newsml_BRE9A605" with "publish" type and "published" state
        Then we get OK response
        When we get "/published/tag:example.com,0000:newsml_BRE9A605"
        Then we get OK response
        When we patch "/users/#CONTEXT_USER_ID#"
        """
        {"user_type": "user", "privileges": {"archive": 1, "unlock": 1, "tasks": 1, "users": 1}}
        """
        Then we get OK response
        When we expire items
        """
        ["tag:example.com,0000:newsml_BRE9A605"]
        """
        When we get "/archived"
        Then we get list with 1 items
        When we delete "/archived/tag:example.com,0000:newsml_BRE9A605:2"
        Then we get response code 403
        When we get "/archived"
        Then we get list with 1 items