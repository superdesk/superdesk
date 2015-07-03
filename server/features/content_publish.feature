Feature: Content Publishing

    @auth
    Scenario: Publish a user content
      Given the "validators"
      """
      [{"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
      """
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And "archive"
      """
      [{"guid": "123", "type": "text", "headline": "test", "_current_version": 1, "state": "fetched",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
        "body_html": "Test Document body"}]
      """
      When we post to "/subscribers" with success
      """
      {
        "name":"Channel 3","media_type":"media", "can_send_takes_packages": true, "sequence_num_settings":{"min" : 1, "max" : 10},
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

    @auth
    @vocabulary
    Scenario: Publish a user content passes the filter
      Given the "validators"
      """
      [{"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
      """
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And "archive"
      """
      [{"guid": "123", "type": "text", "headline": "test", "_current_version": 1, "state": "fetched",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
        "body_html": "Test Document body"}]
      """
      Given empty "filter_conditions"
      When we post to "/filter_conditions" with success
      """
      [{"name": "sport", "field": "headline", "operator": "like", "value": "est"}]
      """
      Then we get latest
      Given empty "publish_filters"
      When we post to "/publish_filters" with success
      """
      [{"publish_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer-only"}]
      """
      When we post to "/subscribers" with success
      """
      {
        "name":"Channel 3","media_type":"media",
        "can_send_takes_packages": true,
        "sequence_num_settings":{"min" : 1, "max" : 10},
        "publish_filter":{"filter_id":"#publish_filters._id#", "filter_type": "permitting"},
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
      }
      """
      Then we get latest
      When we publish "#archive._id#" with "publish" type and "published" state
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
      When we get "/publish_queue"
      Then we get list with 1 items


    @auth
    @vocabulary
    Scenario: Publish a user content blocked by the filter
      Given the "validators"
      """
      [{"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
      """
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And "archive"
      """
      [{"guid": "123", "type": "text", "headline": "test", "_current_version": 1, "state": "fetched",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
        "body_html": "Test Document body"}]
      """

      Given empty "filter_conditions"
      When we post to "/filter_conditions" with success
      """
      [{"name": "sport", "field": "headline", "operator": "like", "value": "est"}]
      """

      Then we get latest
      Given empty "publish_filters"
      When we post to "/publish_filters" with success
      """
      [{"publish_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer-only"}]
      """
      When we post to "/subscribers" with success
      """
      {
        "name":"Channel 3","media_type":"media",
        "can_send_takes_packages": true,
        "sequence_num_settings":{"min" : 1, "max" : 10},
        "publish_filter":{"filter_id":"#publish_filters._id#", "filter_type": "blocking"},
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
      }
      """

      Then we get latest
      When we publish "#archive._id#" with "publish" type and "published" state
      Then we get response code 400
      When we get "/publish_queue"
      Then we get list with 0 items

    @auth
    Scenario: Publish user content that fails validation
      Given the "validators"
      """
      [{"_id": "publish_text", "act": "publish", "type": "text", "schema":{"headline": {"required": true}}}]
      """
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And "archive"
      """
      [{"guid": "123", "_current_version": 1, "state": "fetched",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
        "body_html": "Test Document body"}]
      """
      When we publish "#archive._id#" with "publish" type and "published" state
      Then we get response code 400
      """
        {"_issues": {"validator exception": "Publish failed due to {'headline': 'required field'}"}, "_status": "ERR"}
      """

    @auth
    Scenario: Publish a user content fails if content format is not compatible
      Given the "validators"
      """
      [{"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
      """
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And "archive"
      """
      [{"guid": "123", "type": "image", "headline": "test", "_current_version": 1, "state": "fetched",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
        "body_html": "Test Document body"}]
      """
      When we post to "/subscribers" with success
      """
      {
        "name":"Channel 3","media_type":"media", "can_send_takes_packages": true, "sequence_num_settings":{"min" : 1, "max" : 10},
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
      }
      """
      And we publish "#archive._id#" with "publish" type and "published" state
      Then we get response code 400
      """
      {"_issues": {"validator exception": "500: Failed to publish the item: PublishQueueError Error 9009 - Item could not be queued"}}
      """

    @auth
    Scenario: Schedule a user content publish
      Given empty "subscribers"
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And the "validators"
      """
      [{"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
      """
      And "archive"
      """
      [{"guid": "123", "headline": "test", "_current_version": 1, "state": "fetched",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
        "publish_schedule":"2016-05-30T10:00:00+00:00",
        "body_html": "Test Document body"}]
      """
      When we post to "/subscribers" with success
      """
      {
        "name":"Channel 3","media_type":"media", "can_send_takes_packages": true, "sequence_num_settings":{"min" : 1, "max" : 10},
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
      }
      """
      And we publish "#archive._id#" with "publish" type and "published" state
      Then we get OK response
      And we get existing resource
      """
      {"_current_version": 2, "state": "scheduled", "operation": "publish"}
      """

      When we get "/publish_queue"
      Then we get list with 1 items
      """
      {
        "_items":
          [
            {"destination":{"name":"Test"}, "publish_schedule":"2016-05-30T10:00:00+0000"}
          ]
      }
      """

    @auth
    Scenario: Deschedule an item
      Given empty "subscribers"
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And the "validators"
      """
      [{"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
      """
      And "archive"
      """
      [{"guid": "123", "headline": "test", "_current_version": 1, "state": "fetched",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
        "publish_schedule":"2016-05-30T10:00:00+00:00",
        "body_html": "Test Document body"}]
      """
      When we post to "/subscribers" with success
      """
      {
        "name":"Channel 3","media_type":"media", "can_send_takes_packages": true, "sequence_num_settings":{"min" : 1, "max" : 10},
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
      }
      """
      And we publish "#archive._id#" with "publish" type and "published" state
      Then we get OK response
      And we get existing resource
      """
      {"_current_version": 2, "state": "scheduled"}
      """
      When we get "/publish_queue"
      Then we get list with 1 items
      """
      {
        "_items":
          [
            {"destination":{"name":"Test"}, "publish_schedule":"2016-05-30T10:00:00+0000"}
          ]
      }
      """
      When we patch "/archive/123"
      """
      {"publish_schedule": "2017-05-30T10:00:00+00:00"}
      """
      And we get "/archive"
      Then we get existing resource
      """
      {
          "_items": [
              {
                  "_current_version": 3,
                  "state": "in_progress"
              }
          ]
      }
      """
      When we get "/publish_queue"
      Then we get list with 0 items
      When we get "/published"
      Then we get list with 0 items

    @auth
    Scenario: Deschedule an item fails if date is past
      Given empty "subscribers"
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And "archive"
      """
      [{"guid": "123", "headline": "test", "_current_version": 1, "state": "fetched",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
        "body_html": "Test Document body"}]
      """
      When we post to "/subscribers" with success
      """
      {
        "name":"Channel 3","media_type":"media", "can_send_takes_packages": true, "sequence_num_settings":{"min" : 1, "max" : 10},
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
      }
      """
      And we patch "/archive/123"
      """
      {"publish_schedule": "2010-05-30T10:00:00+00:00"}
      """
      Then we get response code 400

    @auth
    Scenario: Publish a user content and stays on the same stage
      Given "desks"
      """
      [{"name": "Sports"}]
      """
      And the "validators"
      """
      [{"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
      """
      And "archive"
      """
      [{"guid": "123", "headline": "test", "_current_version": 1, "state": "fetched",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
        "body_html": "Test Document body"}]
      """
      When we post to "/subscribers" with success
      """
      {
        "name":"Channel 3","media_type":"media", "can_send_takes_packages": true, "sequence_num_settings":{"min" : 1, "max" : 10},
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
      }
      """
      When we publish "#archive._id#" with "publish" type and "published" state
      Then we get OK response
      And we get existing resource
      """
      {"_current_version": 2, "state": "published", "task":{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}
      """

    @auth
    Scenario: Clean autosave on publishing item
      Given the "validators"
      """
      [{"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
      """
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And "archive"
      """
      [{"guid": "123", "headline": "test", "_current_version": 1, "state": "fetched",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
        "body_html": "Test Document body"}]
      """
      When we post to "/subscribers" with success
      """
      {
        "name":"Channel 3","media_type":"media", "can_send_takes_packages": true, "sequence_num_settings":{"min" : 1, "max" : 10},
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
      }
      """
      And we post to "/archive_autosave"
      """
      {"_id": "#archive._id#", "guid": "123", "headline": "testing", "state": "fetched"}
      """
      Then we get existing resource
      """
      {"_id": "#archive._id#", "guid": "123", "headline": "testing", "_current_version": 1, "state": "fetched",
      "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}
      """
      When we publish "#archive._id#" with "publish" type and "published" state
      Then we get OK response
      When we get "/archive_autosave/#archive._id#"
      Then we get error 404

    @auth
    Scenario: We can lock a published content and then kill it
      Given the "validators"
      """
      [{"_id": "publish_text", "act": "publish", "type": "text", "schema":{}},
      {"_id": "kill_text", "act": "kill", "type": "text", "schema":{}}]
      """
      And "desks"
      """
      [{"name": "Sports", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
      """
      And "archive"
      """
      [{"guid": "123", "headline": "test", "_current_version": 1, "state": "fetched",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
        "body_html": "Test Document body"}]
      """
      When we post to "/subscribers" with success
      """
      {
        "name":"Channel 3","media_type":"media", "can_send_takes_packages": true, "sequence_num_settings":{"min" : 1, "max" : 10},
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
      }
      """
      And we publish "#archive._id#" with "publish" type and "published" state
      Then we get OK response
      When we post to "/archive/#archive._id#/lock"
      """
      {}
      """
      Then we get OK response
      When we publish "#archive._id#" with "kill" type and "killed" state
      Then we get OK response
      And we get existing resource
      """
      {"_current_version": 4, "state": "killed", "operation": "kill", "task":{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}
      """
      When we post to "/archive/#archive._id#/unlock"
      """
      {}
      """
      Then we get OK response

    @auth
    Scenario: We can lock a published content and then correct it
      Given the "validators"
      """
      [{"_id": "publish_text", "act": "publish", "type": "text", "schema":{}},
      {"_id": "correct_text", "act": "correct", "type": "text", "schema":{}}]
      """
      And "desks"
      """
      [{"name": "Sports", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
      """
      And "archive"
      """
      [{"guid": "123", "headline": "test", "_current_version": 1, "state": "fetched",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
        "body_html": "Test Document body"}]
      """
      When we post to "/subscribers" with success
      """
      {
        "name":"Channel 3","media_type":"media", "can_send_takes_packages": true, "sequence_num_settings":{"min" : 1, "max" : 10},
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
      }
      """
      And we publish "#archive._id#" with "publish" type and "published" state
      Then we get OK response
      When we post to "/archive/#archive._id#/lock"
      """
      {}
      """
      Then we get OK response
      When we publish "#archive._id#" with "correct" type and "corrected" state
      Then we get OK response
      And we get existing resource
      """
      {"_current_version": 4, "state": "corrected", "operation": "correct", "task":{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}
      """
      When we post to "/archive/#archive._id#/unlock"
      """
      {}
      """
      Then we get OK response

    @auth
    Scenario: Correcting an already corrected published story fails
      Given the "validators"
      """
      [{"_id": "publish_text", "act": "publish", "type": "text", "schema":{}},
      {"_id": "correct_text", "act": "correct", "type": "text", "schema":{}}]
      """
      And "desks"
      """
      [{"name": "Sports", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
      """
      And "archive"
      """
      [{"guid": "123", "headline": "test", "_current_version": 1, "state": "fetched",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
        "body_html": "Test Document body"}]
      """
      When we post to "/subscribers" with success
      """
      {
        "name":"Channel 3","media_type":"media", "can_send_takes_packages": true, "sequence_num_settings":{"min" : 1, "max" : 10},
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
      }
      """
      And we publish "#archive._id#" with "publish" type and "published" state
      Then we get OK response
      When we post to "/archive/#archive._id#/lock"
      """
      {}
      """
      Then we get OK response
      When we publish "#archive._id#" with "correct" type and "corrected" state
      Then we get OK response
      And we get existing resource
      """
      {"_current_version": 4, "state": "corrected", "task":{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}
      """
      When we publish "#archive._id#" with "publish" type and "published" state
      Then we get response code 400

    @auth
    Scenario: We can correct a corrected story
      Given the "validators"
      """
      [{"_id": "publish_text", "act": "publish", "type": "text", "schema":{}},
      {"_id": "correct_text", "act": "correct", "type": "text", "schema":{}}]
      """
      And "desks"
      """
      [{"name": "Sports", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
      """
      And "archive"
      """
      [{"guid": "123", "headline": "test", "_current_version": 1, "state": "fetched",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
        "body_html": "Test Document body"}]
      """
      When we post to "/subscribers" with success
      """
      {
        "name":"Channel 3","media_type":"media", "can_send_takes_packages": true, "sequence_num_settings":{"min" : 1, "max" : 10},
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
      }
      """
      And we publish "#archive._id#" with "publish" type and "published" state
      Then we get OK response
      When we post to "/archive/#archive._id#/lock"
      """
      {}
      """
      Then we get OK response
      When we publish "#archive._id#" with "correct" type and "corrected" state
      """
      {"headline": "test-1"}
      """
      Then we get OK response
      And we get existing resource
      """
      {"_current_version": 4, "state": "corrected", "task":{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}
      """
      When we publish "#archive._id#" with "correct" type and "corrected" state
      """
      {"headline": "test-2"}
      """
      Then we get OK response
      When we get "/published"
      Then we get existing resource
      """
      {
          "_items": [
              {
                  "headline": "test",
                  "_current_version": 2,
                  "state": "published"
              },
              {
                  "headline": "test-1",
                  "_current_version": 4,
                  "state": "corrected"
              },
              {
                  "headline": "test-2",
                  "_current_version": 5,
                  "state": "corrected"
              }
          ]
      }
      """

    @auth
    Scenario: User can't publish without a privilege
      Given "archive"
      """
      [{"headline": "test", "_current_version": 1, "state": "fetched"}]
      """
      And we login as user "foo" with password "bar"
      """
      {"user_type": "user", "email": "foo.bar@foobar.org"}
      """
      When we publish "#archive._id#" with "publish" type and "published" state
      Then we get response code 403

    @auth
    Scenario: User can't publish a draft item
      Given "archive"
      """
      [{"headline": "test", "_current_version": 1, "state": "draft"}]
      """
      When we publish "#archive._id#" with "publish" type and "published" state
      Then we get response code 400

    @auth
    Scenario: User can't update a published item
      Given the "validators"
      """
      [{"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
      """
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And "archive"
      """
      [{"guid": "123", "headline": "test", "_current_version": 1, "state": "fetched",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
        "body_html": "Test Document body"}]
      """
      When we post to "/subscribers" with success
      """
      {
        "name":"Channel 3","media_type":"media", "can_send_takes_packages": true, "sequence_num_settings":{"min" : 1, "max" : 10},
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
      }
      """
      And we publish "#archive._id#" with "publish" type and "published" state
      Then we get OK response
      When we patch "/archive/#archive._id#"
      """
      {"headline": "updating a published item"}
      """
      Then we get response code 400

    @auth
    @provider
    Scenario: Publish a package
        Given the "validators"
        """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}}]
        """
    	And empty "ingest"
    	And "desks"
        """
        [{"name": "Sports"}]
        """
    	When we fetch from "reuters" ingest "tag_reuters.com_2014_newsml_KBN0FL0NM"
        And we post to "/ingest/#reuters.tag_reuters.com_2014_newsml_KBN0FL0NM#/fetch"
        """
        {
        "desk": "#desks._id#"
        }
        """
		And we get "/archive"
        Then we get list with 6 items
        When we publish "#fetch._id#" with "publish" type and "published" state
        Then we get OK response
		When we get "/published"
        Then we get existing resource
		"""
		{
            "_items": [
                {
                    "_current_version": 2,
                    "state": "published"
                },
                {
                    "_current_version": 2,
                    "groups": [
                        {
                            "refs": [
                                {"itemClass": "icls:text"},
                                {"itemClass": "icls:picture"},
                                {"itemClass": "icls:picture"},
                                {"itemClass": "icls:picture"}
                            ]
                        },
                        {"refs": [{"itemClass": "icls:text"}]}
                    ],
                    "state": "published",
                    "type": "composite"
                },
                {
                    "_current_version": 2,
                    "state": "published"
                },
                {
                    "_current_version": 2,
                    "state": "published"
                },
                {
                    "_current_version": 2,
                    "state": "published"
                },
                {
                    "_current_version": 2,
                    "state": "published"
                }
            ]
        }
		"""

    @auth
    Scenario: Publish the second take before the first fails
      Given the "validators"
      """
        [{"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
      """
      And empty "ingest"
      And "desks"
      """
      [{"name": "Sports"}]
      """
      When we post to "archive"
      """
      [{
          "guid": "123",
          "type": "text",
          "headline": "test1",
          "slugline": "comics",
          "anpa_take_key": "Take",
          "state": "draft",
          "task": {
              "user": "#CONTEXT_USER_ID#"
          },
          "body_html": "Take-1"
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
          "type": "text",
          "headline": "test1=2",
          "slugline": "comics",
          "anpa_take_key": "Take=2",
          "state": "draft",
          "original_creator": "#CONTEXT_USER_ID#"
      }
      """
      When we patch "/archive/#TAKE#"
      """
      {"body_html": "Take-2"}
      """
      And we post to "/archive/#TAKE#/move"
      """
      [{"task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]
      """
      And we get "/archive"
      Then we get list with 3 items
      When we publish "#TAKE#" with "publish" type and "published" state
      Then we get response code 400
      """
      {
          "_issues": {"validator exception": "500: Failed to publish the item: PublishQueueError Error 9006 - Previous take is either not published or killed"}
      }
      """

    @auth
    Scenario: Publish the very first take before the second
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
        "name":"Channel 3","media_type":"media", "can_send_takes_packages": true, "sequence_num_settings":{"min" : 1, "max" : 10},
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
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
          "anpa-category": {"qcode": "A", "name": "Sport"},
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
          "type": "text",
          "headline": "Take-1 headline=2",
          "slugline": "Take-1 slugline",
          "anpa_take_key": "Take=2",
          "state": "draft",
          "original_creator": "#CONTEXT_USER_ID#"
      }
      """
      When we patch "/archive/#TAKE#"
      """
      {"body_html": "Take-2"}
      """
      And we post to "/archive/#TAKE#/move"
      """
      [{"task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]
      """
      And we get "/archive"
      Then we get list with 3 items
      When we publish "123" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get existing resource
      """
      {
          "_items": [
              {
                  "_current_version": 3,
                  "state": "published",
                  "body_html": "Take-1"
              },
              {
                  "_current_version": 2,
                  "state": "published",
                  "type": "composite",
                  "package_type": "takes",
                  "body_html": "Take-1<br>"
              }
          ]
      }
      """

    @auth
    Scenario: Publish the second take after the first
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
        "name":"Channel 3","media_type":"media", "can_send_takes_packages": true, "sequence_num_settings":{"min" : 1, "max" : 10},
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
      }
      """
      When we post to "archive" with success
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
          "anpa-category": {"qcode": "A", "name": "Sport"},
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
          "type": "text",
          "headline": "Take-1 headline=2",
          "slugline": "Take-1 slugline",
          "anpa_take_key": "Take=2",
          "state": "draft",
          "original_creator": "#CONTEXT_USER_ID#"
      }
      """
      When we patch "/archive/#TAKE#"
      """
      {"body_html": "Take-2", "abstract": "Take-2 Abstract"}
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
      When we get "/published"
      Then we get existing resource
      """
      {
          "_items": [
              {
                  "_id": "123",
                  "_current_version": 3,
                  "state": "published",
                  "body_html": "Take-1"
              },
              {
                  "_current_version": 3,
                  "state": "published",
                  "type": "composite",
                  "package_type": "takes",
                  "body_html": "Take-1<br>Take-2<br>"
              },
              {
                  "_current_version": 4,
                  "state": "published",
                  "body_html": "Take-2"
              }
          ]
      }
      """

    @auth
    Scenario: As a user I shouldn't be able to publish an item which is marked as not for publication
      Given "desks"
      """
      [{"name": "Sports"}]
      """
      When we post to "/archive" with success
      """
      [{"guid": "123", "headline": "test", "body_html": "body", "state": "fetched",
        "marked_for_not_publication": true, "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
      """
      And we publish "#archive._id#" with "publish" type and "published" state
      Then we get error 400
      """
      {"_issues": {"validator exception": "400: Cannot publish an item which is marked as Not for Publication"}}
      """

    @auth
    Scenario: Assign a default Source to user created content Items and is overwritten by Source at desk level when published
      Given the "validators"
      """
      [{"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
      """
      And "desks"
      """
      [{"name": "Sports", "source": "Superdesk Sports"}]
      """
      And "archive"
      """
      [{"guid": "123", "headline": "test", "body_html": "body", "_current_version": 1, "state": "fetched",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
      """
      When we post to "/subscribers" with success
      """
      {
        "name":"Channel 3","media_type":"media", "can_send_takes_packages": true, "sequence_num_settings":{"min" : 1, "max" : 10},
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
      }
      """
      And we post to "/stages" with success
      """
      [{"name": "Published Stage", "task_status": "done", "desk": "#desks._id#"}]
      """
      And we publish "#archive._id#" with "publish" type and "published" state
      Then we get OK response
      And we get existing resource
      """
      {"_current_version": 2, "source": "Superdesk Sports", "state": "published", "task":{"desk": "#desks._id#"}}
      """
