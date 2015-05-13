
Feature: Publish Queue

  @auth
  Scenario: Add a new transmission entry to the queue
    Given empty "archive"
    Given empty "formatted_item"
    Given empty "output_channels"
    Given empty "subscribers"
    When we post to "/archive"
    """
    [{"headline": "test"}]
    """
    And we post to "/formatted_item"
    """
    {
      "item_id":"#archive._id#","item_version":"2","formatted_item":"This is the formatted item","format":"nitf"
    }
    """
    Then we get latest
    """
    {
      "format":"nitf"
    }
    """
    When we post to "/subscribers"
    """
    {
      "name":"Channel 3"
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
        "name":"Output Channel", "description": "new stuff",
        "destinations": ["#subscribers._id#"]
      }
    ]
    """
    Then we get latest
    """
    {
      "name":"Output Channel"
    }
    """

    When we post to "/publish_queue" with success
    """
    {
       "item_id":"#archive._id#","publish_schedule": "2016-05-30T10:00:00+00:00", "formatted_item_id":"#formatted_item._id#","output_channel_id":"#output_channels._id#","subscriber_id":"#subscribers._id#","destination":{"name":"destination2","delivery_type":"Email","config":{"password":"abc"}}
    }
    """
    And we get "/publish_queue"
    Then we get list with 1 items
    """
    {
      "_items":
        [
          {"destination":{"name":"destination2"}}
        ]
    }
    """

  @auth
  Scenario: Patch a transmission entry
    Given empty "archive"
    Given empty "formatted_item"
    Given empty "output_channels"
    Given empty "subscribers"
    When we post to "/archive"
    """
    [{"headline": "test"}]
    """
    And we post to "/formatted_item"
    """
    {
      "item_id":"#archive._id#","item_version":"2","formatted_item":"This is the formatted item","format":"nitf"
    }
    """
    Then we get latest
    """
    {
      "format":"nitf"
    }
    """
    When we post to "/subscribers"
    """
    {
      "name":"Channel 3"
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
        "name":"Output Channel", "description": "new stuff",
        "destinations": ["#subscribers._id#"]
      }
    ]
    """
    Then we get latest
    """
    {
      "name":"Output Channel"
    }
    """

    When we post to "/publish_queue" with success
    """
    {
      "item_id":"#archive._id#","formatted_item_id":"#formatted_item._id#","output_channel_id":"#output_channels._id#","subscriber_id":"#subscribers._id#","destination":{"name":"destination2","delivery_type":"Email","config":{"password":"abc"}}
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
      [{"name":"Group 2", "description": "new stuff", "format": "nitf", "destinations": ["#subscribers._id#"]}]
      """
      And we post to "/destination_groups" with "destgroup1" and success
      """
      [{
        "name":"Group 1", "description": "new stuff",
        "destination_groups": [],
        "output_channels": [{"channel":"#channel1#", "selector_codes": ["PXX", "XYZ"]}]
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
      Then we get "published_seq_num" in "/publish_queue/123"
      And we get "published_seq_num" in "/formatted_item/123"
