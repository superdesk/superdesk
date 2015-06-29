Feature: Subscribers

  @auth
  Scenario: Add a new subscriber
    Given empty "subscribers"
    When we get "/subscribers"
    Then we get list with 0 items
    When we post to "/subscribers" with success
    """
    {
      "name":"News1","media_type":"media", "sequence_num_settings":{"min" : 1, "max" : 10},
      "destinations":[{"name":"destination1","format": "nitf", "delivery_type":"FTP","config":{"ip":"144.122.244.55","password":"xyz"}}]
    }
    """
    And we get "/subscribers"
    Then we get list with 1 items
    """
    {"_items":[{"name":"News1"}]}
    """

  @auth
  Scenario: Update a subscriber
    Given empty "subscribers"
    When we post to "/subscribers"
    """
    {
      "name":"News1","media_type":"media", "sequence_num_settings":{"min" : 1, "max" : 10},
      "destinations":[{"name":"destination1","format": "nitf", "delivery_type":"FTP","config":{"ip":"144.122.244.55","password":"xyz"}}]
    }
    """
    And we patch latest
    """
    {"destinations":[{"name":"destination2", "format": "nitf", "delivery_type":"email", "config":{"recipients":"abc@abc.com"}}]}
    """
    Then we get updated response
    """
    {"destinations":[{"name":"destination2", "format": "nitf", "delivery_type":"email", "config":{"recipients":"abc@abc.com"}}]}
    """

  @auth
  Scenario: Deleting a Subscriber is not allowed
    Given empty "subscribers"
    When we post to "/subscribers"
    """
    {
      "name":"News1","media_type":"media", "sequence_num_settings":{"min" : 1, "max" : 10},
      "destinations":[{"name":"destination1","format": "nitf", "delivery_type":"FTP","config":{"ip":"144.122.244.55","password":"xyz"}}]
    }
    """
    When we delete latest
    Then we get error 405

  @auth
  Scenario: Creating a Subscriber should fail when Mandatory properties are not passed for destinations
    Given empty "subscribers"
    When we post to "/subscribers"
    """
    {
      "name":"News1","media_type":"media", "sequence_num_settings":{"min" : 1, "max" : 10},
      "destinations":[{"name": ""}]
    }
    """
    Then we get error 400
    """
    {"_issues": {"destinations": {"0": {
                                        "name": "empty values not allowed",
                                        "format": {"required": 1},
                                        "delivery_type": {"required": 1}}}},
     "_status": "ERR"}
    """

  @auth
  Scenario: Creating a Subscriber with sequence number should fail if min value is less than or equal to 0
    Given empty "subscribers"
    When we post to "/subscribers"
    """
    {
      "name":"News1","media_type":"media", "sequence_num_settings":{"min" : 0, "max" : 10},
      "destinations":[{"name":"destination1","format": "nitf", "delivery_type":"FTP","config":{"ip":"144.122.244.55","password":"xyz"}}]
    }
    """
    Then we get error 400
    """
    {"_issues": {"sequence_num_settings.min": 1}, "_message": "Value of Minimum in Sequence Number Settings should be greater than 0"}
    """
