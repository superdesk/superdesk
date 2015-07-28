Feature: Rewrite content

    @auth
    Scenario: Rewrite a published content
      Given the "validators"
      """
        [
        {
            "schema": {},
            "type": "text",
            "act": "publish",
            "_id": "publish_text"
        },
        {
            "_id": "publish_composite",
            "act": "publish",
            "type": "composite",
            "schema": {}
        }
        ]
      """
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And "archive"
      """
      [{"guid": "123", "type": "text", "headline": "test", "_current_version": 1, "state": "fetched",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
        "subject":[{"qcode": "17004000", "name": "Statistics"}],
        "body_html": "Test Document body"}]
      """
      When we post to "/stages"
      """
      [
        {
        "name": "another stage",
        "description": "another stage",
        "task_status": "in_progress",
        "desk": "#desks._id#"
        }
      ]
      """
      And we post to "/archive/123/move"
        """
        [{"task": {"desk": "#desks._id#", "stage": "#stages._id#"}}]
        """
      Then we get OK response
      When we post to "/subscribers" with success
      """
      {
        "name":"Channel 3","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
      }
      """
      And we publish "#archive._id#" with "publish" type and "published" state
      Then we get OK response
      And we get existing resource
      """
      {"_current_version": 3, "state": "published", "task":{"desk": "#desks._id#", "stage": "#stages._id#"}}
      """
      When we get "/published"
      Then we get existing resource
      """
      {"_items" : [{"_id": "123", "guid": "123", "headline": "test", "_current_version": 3, "state": "published",
        "task": {"desk": "#desks._id#", "stage": "#stages._id#", "user": "#CONTEXT_USER_ID#"}}]}
      """
      When we rewrite "123"
      """
      {"desk_id": "#desks._id#"}
      """
      When we get "/published"
      Then we get existing resource
      """
      {"_items" : [{"_id": "123", "rewritten_by": "#REWRITE_ID#"},
                   {"package_type": "takes", "rewritten_by": "#REWRITE_ID#"}]}
      """
      When we get "/archive"
      Then we get existing resource
      """
      {"_items" : [{"_id": "#REWRITE_ID#", "anpa_take_key": "update", "rewrite_of": "#archive.123.take_package#",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]}
      """

    @auth
    Scenario: Rewrite the non-last take fails
        Given the "validators"
        """
        [{"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
        """
    	And empty "ingest"
    	And "desks"
        """
        [{"name": "Sports"}]
        """
        When we post to "/subscribers" with success
        """
        {
          "name":"News1","media_type":"media", "subscriber_type": "digital",
          "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
          "destinations":[{"name":"destination1","format": "nitf", "delivery_type":"FTP","config":{"ip":"144.122.244.55","password":"xyz"}}]
        }
        """
    	And we post to "archive" with success
        """
        [{
            "guid": "123",
            "type": "text",
            "headline": "Take-1 headline",
            "abstract": "Take-1 abstract",
            "task": {
                "user": "#CONTEXT_USER_ID#"
            },
            "body_html": "Take-1",
            "state": "draft",
            "slugline": "Take-1 slugline",
            "urgency": "4",
            "pubstatus": "usable",
            "subject":[{"qcode": "17004000", "name": "Statistics"}],
            "anpa_category": [{"qcode": "A", "name": "Sport"}],
            "anpa_take_key": "Take"
        }]
        """
        And we post to "/archive/123/move"
        """
        [{"task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]
        """
        Then we get OK response
        When we post to "archive/123/link"
        """
        [{}]
        """
        Then we get next take as "TAKE"
        """
        {
            "_id": "#TAKE#",
            "type": "text",
            "headline": "Take-1 headline",
            "slugline": "Take-1 slugline",
            "anpa_take_key": "Take=2",
            "state": "draft",
            "original_creator": "#CONTEXT_USER_ID#",
            "takes": {
                "_id": "#TAKE_PACKAGE#",
                "package_type": "takes",
                "type": "composite"
            },
            "linked_in_packages": [{"package_type" : "takes","package" : "#TAKE_PACKAGE#"}]
        }
        """
        When we patch "/archive/#TAKE#"
        """
        {"body_html": "Take-2", "abstract": "Take-1 abstract changed"}
        """
        And we post to "/archive/#TAKE#/move"
        """
        [{"task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]
        """
		And we get "/archive"
        Then we get list with 3 items
        When we publish "123" with "publish" type and "published" state
        Then we get OK response
        When we post to "archive/#TAKE#/link"
        """
        [{}]
        """
        Then we get next take as "TAKE2"
        """
        {
            "_id": "#TAKE2#",
            "type": "text",
            "headline": "Take-1 headline",
            "slugline": "Take-1 slugline",
            "anpa_take_key": "Take=3",
            "state": "draft",
            "original_creator": "#CONTEXT_USER_ID#",
            "takes": {
                "_id": "#TAKE_PACKAGE#",
                "package_type": "takes",
                "type": "composite"
            },
            "linked_in_packages": [{"package_type" : "takes","package" : "#TAKE_PACKAGE#"}]
        }
        """
        When we rewrite "123"
        """
        {"desk_id": "#desks._id#"}
        """
        Then we get error 400
        """
        {"_message": "Only last take of the package can be rewritten."}
        """

    @auth
    Scenario: Rewrite the last take succeeds
        Given the "validators"
        """
        [{"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
        """
    	And empty "ingest"
    	And "desks"
        """
        [{"name": "Sports"}]
        """
        When we post to "/subscribers" with success
        """
        {
          "name":"News1","media_type":"media", "subscriber_type": "digital",
          "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
          "destinations":[{"name":"destination1","format": "nitf", "delivery_type":"FTP","config":{"ip":"144.122.244.55","password":"xyz"}}]
        }
        """
    	And we post to "archive" with success
        """
        [{
            "guid": "123",
            "type": "text",
            "headline": "Take-1 headline",
            "abstract": "Take-1 abstract",
            "task": {
                "user": "#CONTEXT_USER_ID#"
            },
            "body_html": "Take-1",
            "state": "draft",
            "slugline": "Take-1 slugline",
            "urgency": "4",
            "pubstatus": "usable",
            "subject":[{"qcode": "17004000", "name": "Statistics"}],
            "anpa_category": [{"qcode": "A", "name": "Sport"}],
            "anpa_take_key": "Take"
        }]
        """
        And we post to "/archive/123/move"
        """
        [{"task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]
        """
        Then we get OK response
        When we post to "archive/123/link"
        """
        [{}]
        """
        Then we get next take as "TAKE"
        """
        {
            "_id": "#TAKE#",
            "type": "text",
            "headline": "Take-1 headline",
            "slugline": "Take-1 slugline",
            "anpa_take_key": "Take=2",
            "state": "draft",
            "original_creator": "#CONTEXT_USER_ID#",
            "takes": {
                "_id": "#TAKE_PACKAGE#",
                "package_type": "takes",
                "type": "composite"
            },
            "linked_in_packages": [{"package_type" : "takes","package" : "#TAKE_PACKAGE#"}]
        }
        """
        When we patch "/archive/#TAKE#"
        """
        {"body_html": "Take-2", "abstract": "Take-1 abstract changed"}
        """
        And we post to "/archive/#TAKE#/move"
        """
        [{"task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]
        """
		And we get "/archive"
        Then we get list with 3 items
        When we publish "123" with "publish" type and "published" state
        Then we get OK response
        When we publish "#TAKE#" with "publish" type and "published" state
        Then we get OK response
        When we rewrite "#TAKE#"
        """
        {"desk_id": "#desks._id#"}
        """
        When we get "/published"
        Then we get existing resource
        """
        {"_items" : [{"_id": "123"},
                     {"package_type": "takes", "rewritten_by": "#REWRITE_ID#"},
                     {"_id": "#TAKE#", "rewritten_by": "#REWRITE_ID#"}]}
        """
        When we get "/archive"
        Then we get existing resource
        """
        {"_items" : [{"_id": "#REWRITE_ID#", "anpa_take_key": "update", "rewrite_of": "#archive.123.take_package#",
          "task": {"desk": "#desks._id#"}}]}
        """

      @auth
      Scenario: Rewrite of a rewritten published content
        Given the "validators"
        """
          [
          {
              "schema": {},
              "type": "text",
              "act": "publish",
              "_id": "publish_text"
          },
          {
              "_id": "publish_composite",
              "act": "publish",
              "type": "composite",
              "schema": {}
          }
          ]
        """
        And "desks"
        """
        [{"name": "Sports"}]
        """
        And "archive"
        """
        [{"guid": "123", "type": "text", "headline": "test", "_current_version": 1, "state": "fetched",
          "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "body_html": "Test Document body"}]
        """
        When we post to "/subscribers" with success
        """
        {
          "name":"Channel 3","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
          "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
        }
        """
        And we publish "#archive._id#" with "publish" type and "published" state
        When we rewrite "123"
        """
        {"desk_id": "#desks._id#"}
        """
        And we patch "archive/#REWRITE_ID#"
        """
        {"abstract": "test", "body_html": "Test Document body"}
        """
        When we publish "#REWRITE_ID#" with "publish" type and "published" state
        When we get "/published"
        Then we get existing resource
        """
        {"_items" : [{"_id": "123", "rewritten_by": "#REWRITE_ID#"},
                     {"package_type": "takes", "rewritten_by": "#REWRITE_ID#"},
                     {"_id": "#REWRITE_ID#", "anpa_take_key": "update"}]}
        """
        When we rewrite "#REWRITE_ID#"
        """
        {"desk_id": "#desks._id#"}
        """
        When we get "/archive"
        Then we get existing resource
        """
        {"_items" : [{"_id": "#REWRITE_ID#", "anpa_take_key": "2nd update",
          "task": {"desk": "#desks._id#"}}]}
        """

    @auth
    Scenario: Spike of an unpublished rewrite removes references
      Given the "validators"
      """
        [
        {
            "schema": {},
            "type": "text",
            "act": "publish",
            "_id": "publish_text"
        },
        {
            "_id": "publish_composite",
            "act": "publish",
            "type": "composite",
            "schema": {}
        }
        ]
      """
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And "archive"
      """
      [{"guid": "123", "type": "text", "headline": "test", "_current_version": 1, "state": "fetched",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
        "subject":[{"qcode": "17004000", "name": "Statistics"}],
        "body_html": "Test Document body"}]
      """
      When we post to "/subscribers" with success
      """
      {
        "name":"Channel 3","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
      }
      """
      And we publish "#archive._id#" with "publish" type and "published" state
      Then we get OK response
      And we get existing resource
      """
      {"_current_version": 2, "state": "published", "task":{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}
      """
      When we get "/published"
      Then we get existing resource
      """
      {"_items" : [{"_id": "123", "guid": "123", "headline": "test", "_current_version": 2, "state": "published",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]}
      """
      When we rewrite "123"
      """
      {"desk_id": "#desks._id#"}
      """
      When we get "/published"
      Then we get existing resource
      """
      {"_items" : [{"_id": "123", "rewritten_by": "#REWRITE_ID#"},
                   {"package_type": "takes", "rewritten_by": "#REWRITE_ID#"}]}
      """
      When we get "/archive"
      Then we get existing resource
      """
      {"_items" : [{"_id": "#REWRITE_ID#", "anpa_take_key": "update", "rewrite_of": "#archive.123.take_package#",
        "task": {"desk": "#desks._id#"}}]}
      """
      When we spike "#REWRITE_ID#"
      Then we get OK response
      And we get spiked content "#REWRITE_ID#"
      And we get "rewrite_of" not populated
      When we get "/published"
      Then we get "rewritten_by" not populated in results

    @auth
    Scenario: Spike of an unpublished rewrite of a rewrite removes references from last rewrite
    Given the "validators"
      """
        [
        {
            "schema": {},
            "type": "text",
            "act": "publish",
            "_id": "publish_text"
        },
        {
            "_id": "publish_composite",
            "act": "publish",
            "type": "composite",
            "schema": {}
        }
        ]
      """
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And "archive"
      """
      [{"guid": "123", "type": "text", "headline": "test", "_current_version": 1, "state": "fetched",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
        "subject":[{"qcode": "17004000", "name": "Statistics"}],
        "body_html": "Test Document body"}]
      """
      When we post to "/subscribers" with success
      """
      {
        "name":"Channel 3","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
      }
      """
      And we publish "#archive._id#" with "publish" type and "published" state
      When we rewrite "123"
      """
      {"desk_id": "#desks._id#"}
      """
      And we patch "archive/#REWRITE_ID#"
      """
      {"abstract": "test", "body_html": "Test Document body"}
      """
      When we publish "#REWRITE_ID#" with "publish" type and "published" state
      When we get "/published"
      Then we get existing resource
      """
      {"_items" : [{"_id": "123", "rewritten_by": "#REWRITE_ID#"},
                   {"package_type": "takes", "rewritten_by": "#REWRITE_ID#"},
                   {"_id": "#REWRITE_ID#", "anpa_take_key": "update"}]}
      """
      When we rewrite "#REWRITE_ID#"
      """
      {"desk_id": "#desks._id#"}
      """
      When we get "/archive"
      Then we get existing resource
      """
      {"_items" : [{"_id": "#REWRITE_ID#", "anpa_take_key": "2nd update",
        "task": {"desk": "#desks._id#"}}]}
      """
      When we spike "#REWRITE_ID#"
      Then we get OK response
      And we get spiked content "#REWRITE_ID#"
      And we get "rewrite_of" not populated
      When we get "/published"
      Then we get existing resource
      """
      {"_items": [{"_id": "123", "rewritten_by": "#REWRITE_OF#"}]}
      """



      @auth
      Scenario: A new take on a rewritten story fails
        Given the "validators"
        """
          [
          {
              "schema": {},
              "type": "text",
              "act": "publish",
              "_id": "publish_text"
          },
          {
              "_id": "publish_composite",
              "act": "publish",
              "type": "composite",
              "schema": {}
          }
          ]
        """
        And "desks"
        """
        [{"name": "Sports"}]
        """
        And "archive"
        """
        [{"guid": "123", "type": "text", "headline": "test", "_current_version": 1, "state": "fetched",
          "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "body_html": "Test Document body"}]
        """
        When we post to "/subscribers" with success
        """
        {
          "name":"Channel 3","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
          "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
        }
        """
        And we publish "#archive._id#" with "publish" type and "published" state
        When we rewrite "123"
        """
        {"desk_id": "#desks._id#"}
        """
        And we patch "archive/#REWRITE_ID#"
        """
        {"abstract": "test", "body_html": "Test Document body"}
        """
        When we publish "#REWRITE_ID#" with "publish" type and "published" state
        When we get "/published"
        Then we get existing resource
        """
        {"_items" : [{"_id": "123", "rewritten_by": "#REWRITE_ID#"},
                     {"package_type": "takes", "rewritten_by": "#REWRITE_ID#"},
                     {"_id": "#REWRITE_ID#", "anpa_take_key": "update"}]}
        """
        When we post to "archive/123/link"
        """
        [{}]
        """
        Then we get error 400
        """
        {"_message": "Article has been rewritten before !"}
        """

        @auth
        Scenario: A new take on a published rewrite succeeds
        Given the "validators"
        """
          [
          {
              "schema": {},
              "type": "text",
              "act": "publish",
              "_id": "publish_text"
          },
          {
              "_id": "publish_composite",
              "act": "publish",
              "type": "composite",
              "schema": {}
          }
          ]
        """
        And "desks"
        """
        [{"name": "Sports"}]
        """
        And "archive"
        """
        [{"guid": "123", "type": "text", "headline": "test", "_current_version": 1, "state": "fetched",
          "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "body_html": "Test Document body"}]
        """
        When we post to "/subscribers" with success
        """
        {
          "name":"Channel 3","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
          "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
        }
        """
        And we publish "#archive._id#" with "publish" type and "published" state
        When we rewrite "123"
        """
        {"desk_id": "#desks._id#"}
        """
        And we patch "archive/#REWRITE_ID#"
        """
        {"abstract": "test", "body_html": "Test Document body", "headline": "RETAKE", "slugline": "RETAKE"}
        """
        When we publish "#REWRITE_ID#" with "publish" type and "published" state
        When we get "/published"
        Then we get existing resource
        """
        {"_items" : [{"_id": "123", "rewritten_by": "#REWRITE_ID#"},
                     {"package_type": "takes", "rewritten_by": "#REWRITE_ID#"},
                     {"_id": "#REWRITE_ID#", "anpa_take_key": "update"}]}
        """
        When we post to "archive/#REWRITE_ID#/link"
        """
        [{}]
        """
        Then we get next take as "TAKE"
        """
        {
            "_id": "#TAKE#",
            "type": "text",
            "headline": "RETAKE",
            "slugline": "RETAKE",
            "anpa_take_key": "update (reopens)",
            "state": "draft",
            "original_creator": "#CONTEXT_USER_ID#",
            "takes": {
                "_id": "#TAKE_PACKAGE#",
                "package_type": "takes",
                "type": "composite"
            },
            "linked_in_packages": [{"package_type" : "takes","package" : "#TAKE_PACKAGE#"}]
        }
        """