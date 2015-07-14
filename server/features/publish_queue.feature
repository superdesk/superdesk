Feature: Publish Queue

  @auth
  Scenario: Add a new transmission entry to the queue
    Given empty "archive"
    And empty "subscribers"
    When we post to "/archive"
    """
    [{"headline": "test"}]
    """
    And we post to "/subscribers" with success
    """
    {
      "name":"Channel 3","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
      "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
    }
    """
    And we post to "/publish_queue" with success
    """
    {
       "item_id":"#archive._id#","publish_schedule": "2016-05-30T10:00:00+00:00", "subscriber_id":"#subscribers._id#",
       "destination":{"name":"Test","format": "nitf","delivery_type":"email","config":{"recipients":"test@test.com"}}
    }
    """
    And we get "/publish_queue"
    Then we get list with 1 items
    """
    {
      "_items":
        [
          {"destination":{"name":"Test"}}
        ]
    }
    """

  @auth
  Scenario: Patch a transmission entry
    Given empty "archive"
    And empty "subscribers"
    When we post to "/archive"
    """
    [{"headline": "test"}]
    """
    And we post to "/subscribers" with success
    """
    {
      "name":"Channel 3","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
      "destinations":[{"name":"destination2","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
    }
    """
    And we post to "/publish_queue" with success
    """
    {
      "item_id":"#archive._id#","subscriber_id":"#subscribers._id#",
      "destination":{"name":"destination2","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}
    }
    """
    And we get "/publish_queue"
    Then we get list with 1 items
    """
    {
      "_items":
        [
          {"state":"pending"}
        ]
    }
    """
    When we patch "/publish_queue/#publish_queue._id#"
    """
    {
      "state": "in-progress"
    }
    """
    And we get "/publish_queue"
    Then we get list with 1 items
    """
    {
      "_items":
        [
          {"state":"in-progress"}
        ]
    }
    """

  @auth
  Scenario: Published Item should have published sequence number when published and placed in queue
      Given the "validators"
      """
      [{"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
      """
      And "desks"
      """
      [{"name": "Sports"}]
      """
      When we post to "/subscribers" with success
      """
      {
        "name":"Channel 3","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
        "destinations":[{"name":"destination2","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
      }
      """
      And we post to "/archive" with success
      """
      [{"guid": "123", "headline": "test", "body_html": "body", "state": "fetched",
        "subject":[{"qcode": "17004000", "name": "Statistics"}],
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
      """
      And we post to "/stages" with success
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
      And we publish "#archive._id#" with "publish" type and "published" state
      Then we get "published_seq_num" in "/publish_queue/#archive.123.take_package#"

  @auth @notification
  Scenario: Creating a new publish queue entry should add published sequence number
    Given empty "archive"
    And empty "subscribers"
    When we post to "/archive"
    """
    [{"headline": "test"}]
    """
    When we post to "/subscribers" with success
    """
    {
      "name":"Channel 3","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
      "destinations":[{"name":"destination2","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
    }
    """
    And we post to "/publish_queue"
    """
    {
       "item_id":"#archive._id#","publish_schedule": "2016-05-30T10:00:00+00:00", "subscriber_id":"#subscribers._id#",
       "destination":{"name":"destination2","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}
    }
    """
    Then we get "published_seq_num" in "/publish_queue/#archive._id#"
    When we patch "/publish_queue/#publish_queue._id#"
    """
    {"state": "success"}
    """
    Then we get latest
    """
    {"state": "success"}
    """
    And we get notifications
    """
    [{"event": "publish_queue:update", "extra": {"queue_id": "#publish_queue._id#", "state": "success"}}]
    """