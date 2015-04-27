
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
       "item_id":"#archive._id#","formatted_item_id":"#formatted_item._id#","output_channel_id":"#output_channels._id#","subscriber_id":"#subscribers._id#","destination":{"name":"destination2","delivery_type":"Email","config":{"password":"abc"}}
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

