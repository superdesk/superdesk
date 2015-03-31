
Feature: Output Channels

  @auth
  Scenario: Add an output channel
    Given empty "output_channels"
    When we get "/output_channels"
    Then we get list with 0 items
    When we post to "/output_channels"
    """
    {
      "name":"test", "description": "new stuff"
    }
    """
    And we get "/output_channels"
    Then we get list with 1 items
    """
    {
      "_items":
        [
          {"name": "test", "description": "new stuff"}
        ]
    }
    """

  @auth
  Scenario: Update an output channel
    Given "output_channels"
    """
    [{"name":"test", "description": "new stuff"}]
    """
    When we post to "/output_channels"
    """
    {
      "name":"test2", "description": "new stuff2"
    }
    """
    And we patch latest
    """
    {"name":"testing", "description": "stuff"}
    """
    Then we get updated response
    """
    {"name":"testing", "description": "stuff"}
    """

  @auth
  Scenario: Delete an output channel
    Given "output_channels"
    """
    [{"name":"Channel 1", "description": "new stuff"}]
    """
    When we post to "/output_channels"
    """
    {
      "name":"Channel 2", "description": "new stuff2"
    }
    """
    Then we get latest
    """
    {
      "name":"Channel 2", "description": "new stuff2"
    }
    """
    When we delete latest
    Then we get deleted response
    When we post to "/output_channels"
    """
    {
      "name":"Channel 3", "description": "new stuff3"
    }
    """
    Then we get latest
    """
    {
      "name":"Channel 3", "description": "new stuff3"
    }
    """
    When we post to "/destination_groups"
    """
    [
      {
        "name":"Destination Group", "description": "new stuff",
        "output_channels": [{"channel": "#output_channels._id#"}]
      }
    ]
    """
    When we delete "/output_channels/#output_channels._id#"
    Then we get error 412
    """
    {"_message":"Output Channel is associated with Destination Groups.", "_status": "ERR"}
    """
