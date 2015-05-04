Feature: Content Publishing

    @auth
    Scenario: Publish a user content and moves to publish stage
      Given "desks"
      """
      [{"name": "Sports"}]
      """
      And we have "/destination_groups" with "destgroup1" and success
      """
      [
        {
          "name":"Group 1", "description": "new stuff",
          "destination_groups": [], "output_channels": []
        }
      ]
      """
      Given "archive"
      """
      [{"guid": "123", "headline": "test", "_version": 1, "state": "fetched", "destination_groups":["#destgroup1#"],
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
      """

      When we post to "/stages" with success
      """
      [
        {
        "name": "another stage",
        "description": "another stage",
        "task_status": "in_progress",
        "desk": "#desks._id#",
        "published_stage": true
        }
      ]
      """
      And we publish "#archive._id#" with "publish" type and "published" state
      Then we get OK response
      And we get existing resource
      """
      {"_version": 2, "state": "published", "task":{"desk": "#desks._id#", "stage": "#stages._id#"}}
      """


    @auth
    Scenario: Schedule a user content publish
      Given empty "output_channels"
      Given empty "subscribers"
      Given "desks"
      """
      [{"name": "Sports"}]
      """
      When we post to "/subscribers"
      """
      {
        "name":"Channel 3", "destinations": [{"name": "Test", "delivery_type": "email", "config": {}}]
      }
      """
      Then we get latest
      """
      {
        "name":"Channel 3"
      }
      """
      When we post to "/output_channels"
      """
      [
        {
          "name":"Output Channel",
          "description": "new stuff",
          "destinations": ["#subscribers._id#"],
          "format": "nitf"
        }
      ]
      """
      Then we get latest
      """
      {
        "name":"Output Channel"
      }
      """

      Given we have "/destination_groups" with "destgroup1" and success
      """
      [
        {
          "name":"Group 1", "description": "new stuff",
          "destination_groups": [], "output_channels": [{"channel": "#output_channels._id#"}]
        }
      ]
      """
      Given "archive"
      """
      [{"guid": "123", "headline": "test", "_version": 1, "state": "fetched", "destination_groups":["#destgroup1#"],
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
        "publish_schedule":"2015-05-30T10:00:00+00:00",
        "body_html": "Test Document body"}]
      """
      When we publish "#archive._id#" with "publish" type and "published" state
      Then we get OK response
      And we get existing resource
      """
      {"_version": 2, "state": "scheduled"}
      """

      When we get "/publish_queue"
      Then we get list with 1 items
      """
      {
        "_items":
          [
            {"destination":{"name":"Test"}, "publish_schedule":"2015-05-30T10:00:00+0000"}
          ]
      }
      """

    @auth
    Scenario: Deschedule an item
        Given empty "output_channels"
      Given empty "subscribers"
      Given "desks"
      """
      [{"name": "Sports"}]
      """
      When we post to "/subscribers"
      """
      {
        "name":"Channel 3", "destinations": [{"name": "Test", "delivery_type": "email", "config": {}}]
      }
      """
      Then we get latest
      """
      {
        "name":"Channel 3"
      }
      """
      When we post to "/output_channels"
      """
      [
        {
          "name":"Output Channel",
          "description": "new stuff",
          "destinations": ["#subscribers._id#"],
          "format": "nitf"
        }
      ]
      """
      Then we get latest
      """
      {
        "name":"Output Channel"
      }
      """

      Given we have "/destination_groups" with "destgroup1" and success
      """
      [
        {
          "name":"Group 1", "description": "new stuff",
          "destination_groups": [], "output_channels": [{"channel": "#output_channels._id#"}]
        }
      ]
      """
      Given "archive"
      """
      [{"guid": "123", "headline": "test", "_version": 1, "state": "fetched", "destination_groups":["#destgroup1#"],
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"},
        "publish_schedule":"2015-05-30T10:00:00+00:00",
        "body_html": "Test Document body"}]
      """
      When we publish "#archive._id#" with "publish" type and "published" state
      Then we get OK response
      And we get existing resource
      """
      {"_version": 2, "state": "scheduled"}
      """

      When we get "/publish_queue"
      Then we get list with 1 items
      """
      {
        "_items":
          [
            {"destination":{"name":"Test"}, "publish_schedule":"2015-05-30T10:00:00+0000"}
          ]
      }
      """
      When we patch "/archive/123"
      """
      {"publish_schedule": "2010-05-30T10:00:00+00:00"}
      """
      And we get "/archive"
      Then we get existing resource
      """
      {
          "_items": [
              {
                  "_version": 3,
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
    Scenario: Publish a user content and stays on the same stage
      Given "desks"
      """
      [{"name": "Sports"}]
      """
      And we have "/destination_groups" with "destgroup1" and success
      """
      [
        {
          "name":"Group 1", "description": "new stuff",
          "destination_groups": [], "output_channels": []
        }
      ]
      """
      And "archive"
      """
      [{"guid": "123", "headline": "test", "_version": 1, "state": "fetched", "destination_groups": ["#destgroup1#"],
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
      """
      When we publish "#archive._id#" with "publish" type and "published" state
      Then we get OK response
      And we get existing resource
      """
      {"_version": 2, "state": "published", "task":{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}
      """

    @auth
    Scenario: Clean autosave on publishing item
        Given "desks"
          """
          [{"name": "Sports"}]
          """
        And we have "/destination_groups" with "destgroup1" and success
          """
          [
            {
              "name":"Group 1", "description": "new stuff",
              "destination_groups": [], "output_channels": []
            }
          ]
          """
        And "archive"
          """
          [{"guid": "123", "headline": "test", "_version": 1, "state": "fetched", "destination_groups": ["#destgroup1#"],
            "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
          """
        When we post to "/archive_autosave"
          """
            {"_id": "#archive._id#", "guid": "123", "headline": "testing", "state": "fetched", "destination_groups": ["#destgroup1#"]}
          """
        Then we get existing resource
          """
            {"_id": "#archive._id#", "guid": "123", "headline": "testing", "_version": 1, "state": "fetched", "destination_groups": ["#destgroup1#"],
            "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}
          """
        When we publish "#archive._id#" with "publish" type and "published" state
        Then we get OK response
        When we get "/archive_autosave/#archive._id#"
        Then we get error 404


    @auth
    Scenario: We can lock a published content and then kill it
      Given "desks"
      """
      [{"name": "Sports", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
      """
      And we have "/destination_groups" with "destgroup1" and success
      """
      [
        {
          "name":"Group 1", "description": "new stuff",
          "destination_groups": [], "output_channels": []
        }
      ]
      """
      Given "archive"
      """
      [{"guid": "123", "headline": "test", "_version": 1, "state": "fetched", "destination_groups": ["#destgroup1#"],
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
      """
      When we publish "#archive._id#" with "publish" type and "published" state
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
      {"_version": 3, "state": "killed", "task":{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}
      """
      When we post to "/archive/#archive._id#/unlock"
      """
        {}
      """
      Then we get OK response


    @auth
    Scenario: User can't publish without a privilege
      Given "archive"
      """
      [{"headline": "test", "_version": 1, "state": "fetched"}]
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
      [{"headline": "test", "_version": 1, "state": "draft"}]
      """
      When we publish "#archive._id#" with "publish" type and "published" state
      Then we get response code 400

    @auth
    Scenario: User can't update a published item
      Given "desks"
      """
      [{"name": "Sports"}]
      """
      And we have "/destination_groups" with "destgroup1" and success
      """
      [
        {
          "name":"Group 1", "description": "new stuff",
          "destination_groups": [], "output_channels": []
        }
      ]
      """
      And "archive"
      """
      [{"guid": "123", "headline": "test", "_version": 1, "state": "fetched", "destination_groups": ["#destgroup1#"],
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
      """
      When we publish "#archive._id#" with "publish" type and "published" state
      Then we get OK response
      When we patch "/archive/#archive._id#"
      """
      {"headline": "updating a published item"}
      """
      Then we get response code 400

    @auth
    @provider
    Scenario: Publish a package
    	Given empty "ingest"
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
                    "_version": 2,
                    "state": "published"
                },
                {
                    "_version": 2,
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
                    "_version": 2,
                    "state": "published"
                },
                {
                    "_version": 2,
                    "state": "published"
                },
                {
                    "_version": 2,
                    "state": "published"
                },
                {
                    "_version": 2,
                    "state": "published"
                }
            ]
        }
		"""
