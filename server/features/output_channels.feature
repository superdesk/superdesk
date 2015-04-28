Feature: Output Channels

  @auth
  Scenario: Create an output channel
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
  Scenario: Create an output channel with sequence number
    Given empty "output_channels"
    When we post to "/output_channels"
    """
    {
      "name":"test oc", "sequence_num_settings": {"min": 1, "max": 99, "start_from": 1}
    }
    """
    And we get "/output_channels"
    Then we get list with 1 items
    """
    {
      "_items":
        [
          {"name":"test oc", "sequence_num_settings": {"min": 1, "max": 99, "start_from": 1}}
        ]
    }
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

  @auth
  Scenario: Deleting an output channel should fail when associated with Destination Group(s)
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

  @auth
  Scenario: Create an output channel with sequence number should fail if min value is less than or equal to 0
    Given empty "output_channels"
    When we post to "/output_channels"
    """
    {
      "name":"test oc", "sequence_num_settings": {"min": 0, "max": 99, "start_from": 1}
    }
    """
    Then we get error 400
    """
    {"_issues": {"sequence_num_settings.min": 1}, "_message": "Value of Minimum in Sequence Number Settings should be greater than 0"}
    """

  @auth
  Scenario: Updating an output channel with invalid start_from in sequence number setting should fail
    Given empty "output_channels"
    When we post to "/output_channels"
    """
    {
      "name":"test oc", "sequence_num_settings": {"min": 1, "max": 99, "start_from": 1}
    }
    """
    And we patch "/output_channels/#output_channels._id#"
    """
    {"sequence_num_settings": {"min": 1, "max": 99, "start_from": 100}}
    """
    Then we get error 400
    """
    {"_issues": {"validator exception": "400: Value of Start From in Sequence Number Settings should be between Minimum and Maximum"}}
    """
