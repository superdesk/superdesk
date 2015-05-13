Feature: Content Publishing

    @auth
    Scenario: Publish a user content and moves to publish stage
      Given the "validators"
      """
      [{"_id": "publish", "schema":{}}]
      """
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
    Scenario: Publish user content that fails validation
      Given the "validators"
      """
      [{"_id": "publish", "schema":{"headline": {"required": true}}}]
      """
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
      [{"guid": "123", "_version": 1, "state": "fetched", "destination_groups":["#destgroup1#"],
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
      Then we get response code 400
      """
        {"_issues": {"validator exception": "Publish failed due to {'headline': 'required field'}"}, "_status": "ERR"}
      """


    @auth
    Scenario: Schedule a user content publish
      Given empty "output_channels"
      Given empty "subscribers"
      Given "desks"
      """
      [{"name": "Sports"}]
      """
      Given the "validators"
      """
      [{"_id": "publish", "schema":{}}]
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
        "publish_schedule":"2016-05-30T10:00:00+00:00",
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
            {"destination":{"name":"Test"}, "publish_schedule":"2016-05-30T10:00:00+0000"}
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
      Given the "validators"
      """
      [{"_id": "publish", "schema":{}}]
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
        "publish_schedule":"2016-05-30T10:00:00+00:00",
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
    Scenario: Deschedule an item fails if date is past
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
        "body_html": "Test Document body"}]
      """
      When we patch "/archive/123"
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
      Given the "validators"
      """
      [{"_id": "publish", "schema":{}}]
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
        Given the "validators"
        """
          [{"_id": "publish", "schema":{}}]
        """
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
      Given the "validators"
      """
      [{"_id": "publish", "schema":{}},
      {"_id": "kill", "schema":{}}]
      """
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
      Given the "validators"
      """
      [{"_id": "publish", "schema":{}}]
      """
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
        Given the "validators"
        """
          [{"_id": "publish", "schema":{}}]
        """
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

    @auth
    Scenario: Publish the second take before the first fails
        Given the "validators"
        """
          [{"_id": "publish", "schema":{}}]
        """
    	Given empty "ingest"
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
        Then we get next take
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
          [{"_id": "publish", "schema":{}}]
        """
    	Given empty "ingest"
    	And "desks"
        """
        [{"name": "Sports"}]
        """
        When we post to "/subscribers" with success
        """
        [{"destinations" : [{"delivery_type" : "email", "name" : "Self_EMail", "config" : {"recipients" : "test@test.org"}}],
          "name" : "Email Subscriber", "is_active" : true
        }]
        """
        And we post to "/output_channels" with "channel1" and success
        """
        [{"name":"Channel 1", "description": "new stuff", "format": "nitf", "destinations": ["#subscribers._id#"]}]
        """
        And we post to "/output_channels" with "channel2" and success
        """
        [{"name":"Channel 2", "description": "new stuff", "format": "nitf", "destinations": ["#subscribers._id#"], "is_active": false}]
        """
        And we post to "/destination_groups" with "destgroup1" and success
        """
        [{
          "name":"Group 1", "description": "new stuff",
          "destination_groups": [],
          "output_channels": [{"channel":"#channel1#", "selector_codes": ["PXX", "XYZ"]}, {"channel":"#channel2#", "selector_codes": []}]
        }]
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
            "destination_groups":["#destgroup1#"],
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
        Then we get next take
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
                    "_version": 3,
                    "state": "published",
                    "body_html": "Take-1"
                },
                {
                    "_version": 2,
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
          [{"_id": "publish", "schema":{}}]
        """
    	Given empty "ingest"
    	And "desks"
        """
        [{"name": "Sports"}]
        """
        When we post to "/subscribers" with success
        """
        [{"destinations" : [{"delivery_type" : "email", "name" : "Self_EMail", "config" : {"recipients" : "test@test.org"}}],
          "name" : "Email Subscriber", "is_active" : true
        }]
        """
        And we post to "/output_channels" with "channel1" and success
        """
        [{"name":"Channel 1", "description": "new stuff", "format": "nitf", "destinations": ["#subscribers._id#"]}]
        """
        And we post to "/output_channels" with "channel2" and success
        """
        [{"name":"Channel 2", "description": "new stuff", "format": "nitf", "destinations": ["#subscribers._id#"], "is_active": false}]
        """
        And we post to "/destination_groups" with "destgroup1" and success
        """
        [{
          "name":"Group 1", "description": "new stuff",
          "destination_groups": [],
          "output_channels": [{"channel":"#channel1#", "selector_codes": ["PXX", "XYZ"]}, {"channel":"#channel2#", "selector_codes": []}]
        }]
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
            "destination_groups":["#destgroup1#"],
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
        Then we get next take
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
        When we publish "#TAKE#" with "publish" type and "published" state
        Then we get OK response
		When we get "/published"
        Then we get existing resource
		"""
		{
            "_items": [
                {
                    "_id": "123",
                    "_version": 3,
                    "state": "published",
                    "body_html": "Take-1"
                },
                {
                    "_version": 3,
                    "state": "published",
                    "type": "composite",
                    "package_type": "takes",
                    "body_html": "Take-1<br>Take-2<br>"
                },
                {
                    "_version": 4,
                    "state": "published",
                    "body_html": "Take-2"
                }
            ]
        }
		"""

    @auth
    @notification
    Scenario: As a user I should be able to publish item to a closed output channel
      Given the "validators"
      """
      [{"_id": "publish", "schema":{}}]
      """
      Given "desks"
      """
      [{"name": "Sports"}]
      """
      When we post to "/subscribers" with success
      """
      [{"destinations" : [{"delivery_type" : "email", "name" : "Self_EMail", "config" : {"recipients" : "test@test.org"}}],
        "name" : "Email Subscriber", "is_active" : true
      }]
      """
      And we post to "/output_channels" with "channel1" and success
      """
      [{"name":"Channel 1", "description": "new stuff", "format": "nitf", "destinations": ["#subscribers._id#"]}]
      """
      And we post to "/output_channels" with "channel2" and success
      """
      [{"name":"Channel 2", "description": "new stuff", "format": "nitf", "destinations": ["#subscribers._id#"], "is_active": false}]
      """
      And we post to "/destination_groups" with "destgroup1" and success
      """
      [{
        "name":"Group 1", "description": "new stuff",
        "destination_groups": [],
        "output_channels": [{"channel":"#channel1#", "selector_codes": ["PXX", "XYZ"]}, {"channel":"#channel2#", "selector_codes": []}]
      }]
      """
      And we post to "/archive" with success
      """
      [{"guid": "123", "headline": "test", "body_html": "body", "state": "fetched", "destination_groups":["#destgroup1#"],
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
      """
      And we post to "/stages" with success
      """
      [
        {"name": "another stage", "description": "another stage", "task_status": "in_progress", "desk": "#desks._id#", "published_stage": true}
      ]
      """
      And we publish "#archive._id#" with "publish" type and "published" state
      Then we get response code 200
      """
      [{"event": "item:publish:closed:channels"}]
      """

    @auth
    Scenario: As a user I shouldn't be able to publish an item which is marked as not for publication
      Given "desks"
      """
      [{"name": "Sports"}]
      """
      When we post to "/subscribers" with success
      """
      [{"destinations" : [{"delivery_type" : "email", "name" : "Self_EMail", "config" : {"recipients" : "test@test.org"}}],
        "name" : "Email Subscriber", "is_active" : true
      }]
      """
      And we post to "/output_channels" with "channel1" and success
      """
      [{"name":"Channel 1", "description": "new stuff", "format": "nitf", "destinations": ["#subscribers._id#"]}]
      """
      And we post to "/output_channels" with "channel2" and success
      """
      [{"name":"Channel 2", "description": "new stuff", "format": "nitf", "destinations": ["#subscribers._id#"], "is_active": false}]
      """
      And we post to "/destination_groups" with "destgroup1" and success
      """
      [{
        "name":"Group 1", "description": "new stuff",
        "destination_groups": [],
        "output_channels": [{"channel":"#channel1#", "selector_codes": ["PXX", "XYZ"]}, {"channel":"#channel2#", "selector_codes": []}]
      }]
      """
      And we post to "/archive" with success
      """
      [{"guid": "123", "headline": "test", "body_html": "body", "state": "fetched", "destination_groups":["#destgroup1#"],
        "marked_for_not_publication": true, "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
      """
      And we post to "/stages" with success
      """
      [
        {"name": "another stage", "description": "another stage", "task_status": "in_progress", "desk": "#desks._id#", "published_stage": true}
      ]
      """
      And we publish "#archive._id#" with "publish" type and "published" state
      Then we get error 400
      """
      {"_issues": {"validator exception": "400: Cannot publish an item which is marked as Not for Publication"}}
      """

    @auth
    Scenario: Assign a default Source to user created content Items and is overwritten by Source at desk level when published
      Given "desks"
      """
      [{"name": "Sports", "source": "Superdesk Sports"}]
      """
      And we have "/destination_groups" with "destgroup1" and success
      """
      [{ "name":"Group 1", "description": "new stuff", "destination_groups": [], "output_channels": [] }]
      """
      Given "archive"
      """
      [{"guid": "123", "headline": "test", "_version": 1, "state": "fetched", "destination_groups":["#destgroup1#"],
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
      """
      When we post to "/stages" with success
      """
      [{"name": "Published Stage", "task_status": "done", "desk": "#desks._id#", "published_stage": true}]
      """
      And we publish "#archive._id#" with "publish" type and "published" state
      Then we get OK response
      And we get existing resource
      """
      {"_version": 2, "source": "Superdesk Sports", "state": "published", "task":{"desk": "#desks._id#", "stage": "#stages._id#"}}
      """
