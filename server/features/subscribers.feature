
Feature: Subscribers

  @auth
  Scenario: Add a new subscriber
    Given empty "subscribers"
    When we get "/subscribers"
    Then we get list with 0 items
    When we post to "/subscribers" with success
    """
    {
      "name":"News1","subscriber_type":"media","destinations":[{"name":"destination1","delivery_type":"FTP","config":{"ip":"144.122.244.55","password":"xyz"}}]
    }
    """
    And we get "/subscribers"
    Then we get list with 1 items
    """
    {
      "_items":
        [
          {"name":"News1"}
        ]
    }
    """

  @auth
  Scenario: Update a subscriber
    Given empty "subscribers"
    When we post to "/subscribers"
    """
    {
      "name":"News1","subscriber_type":"media","destinations":[{"name":"destination1","delivery_type":"FTP","config":{"ip":"144.122.244.55","password":"xyz"}}]
    }
    """
    And we patch latest
    """
    {"destinations":[{"name":"destination2","delivery_type":"Email","config":{"password":"abc"}}]}
    """
    Then we get updated response
    """
    {"destinations":[{"name":"destination2","delivery_type":"Email","config":{"password":"abc"}}]}
    """

  @auth
  Scenario: Delete a subscriber
    Given "subscribers"
    """
    [{"name":"Channel 1"}]
    """
    When we post to "/subscribers"
    """
    {
      "name":"Channel 2"
    }
    """
    Then we get latest
    """
    {
      "name":"Channel 2"
    }
    """
    When we delete latest
    Then we get deleted response
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
    When we post to "/output_channels" with success
    """
    [
      {
        "name":"Output Channel", "description": "new stuff",
        "destinations": ["#subscribers._id#"]
      }
    ]
    """
    When we delete "/subscribers/#subscribers._id#"
    Then we get error 412
    """
    {"_message":"Subscriber is associated with Output Channel.", "_status": "ERR"}
    """

