Feature: Subscribers

  @auth
  Scenario: Add a new subscriber
    Given empty "subscribers"
    When we get "/subscribers"
    Then we get list with 0 items
    When we post to "/subscribers" with success
    """
    {
      "name":"News1","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
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
      "name":"News1","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
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
  @vocabulary
  Scenario: Update a subscriber with publish filter
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "anpa_category", "operator": "in", "value": "4"}]
    """

    Then we get latest
    Given empty "publish_filters"
    When we post to "/publish_filters" with success
    """
    [{"publish_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer-only"}]
    """

    Then we get latest
    Given empty "subscribers"
    When we post to "/subscribers" with success
    """
    {
      "name":"News1","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
      "destinations":[{"name":"destination1","format": "nitf", "delivery_type":"FTP","config":{"ip":"144.122.244.55","password":"xyz"}}]
    }
    """
    And we patch latest
    """
    {"publish_filter":{"filter_id":"#publish_filters._id#"}}
    """
    Then we get updated response
    """
    {"publish_filter":{"filter_id":"#publish_filters._id#", "filter_type":"blocking"}}
    """

  @auth
  @vocabulary
  Scenario: Query subscribers by filter condition
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "anpa_category", "operator": "in", "value": "4"}]
    """
    Then we get latest
    Given empty "publish_filters"
    When we post to "/publish_filters" with success
    """
    [{"publish_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer-only"}]
    """

    Then we get latest
    Given empty "subscribers"
    When we post to "/subscribers" with success
    """
    {
      "name":"News1",
      "media_type":"media",
      "subscriber_type": "digital",
      "sequence_num_settings":{"min" : 1, "max" : 10},
      "email": "test@test.com",
      "destinations":[{"name":"destination1","format": "nitf", "delivery_type":"FTP","config":{"ip":"144.122.244.55","password":"xyz"}}],
      "publish_filter": {"filter_id":"#publish_filters._id#", "filter_type":"blocking"}
    }
    """
    And we get "/subscribers?filter_condition={"field":"anpa_category", "operator":"in", "value":"4"}"
    Then we get list with 1 items
    """
    {"_items":[{"name":"News1"}]}
    """

  @auth
  Scenario: Deleting a Subscriber is not allowed
    Given empty "subscribers"
    When we post to "/subscribers"
    """
    {
      "name":"News1","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
      "destinations":[{"name":"destination1","format": "nitf", "delivery_type":"FTP","config":{"ip":"144.122.244.55","password":"xyz"}}]
    }
    """
    When we delete latest
    Then we get error 405

  @auth
  Scenario: Creating a Subscriber should fail if there are no destinations
    Given empty "subscribers"
    When we post to "/subscribers"
    """
    {
      "name":"News1", "subscriber_type": "digital","media_type":"media", "sequence_num_settings":{"min" : 1, "max" : 10}
    }
    """
    Then we get error 400
    """
    {"_issues": {"destinations": {"required": 1}}, "_status": "ERR"}
    """
    When we post to "/subscribers"
    """
    {
      "name":"News1", "subscriber_type": "digital","media_type":"media", "sequence_num_settings":{"min" : 1, "max" : 10},
      "destinations": []
    }
    """
    Then we get error 400
    """
    {"_issues": {"destinations": {"minlength": 1}}, "_status": "ERR"}
    """

  @auth
  Scenario: Updating a Subscriber with no destinations should fail
    Given empty "subscribers"
    When we get "/subscribers"
    Then we get list with 0 items
    When we post to "/subscribers" with success
    """
    {
      "name":"News1","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
      "destinations":[{"name":"destination1","format": "nitf", "delivery_type":"FTP","config":{"ip":"144.122.244.55","password":"xyz"}}]
    }
    """
    And we get "/subscribers"
    Then we get list with 1 items
    """
    {"_items":[{"name":"News1"}]}
    """
    When we patch "/subscribers/#subscribers._id#"
    """
    {"destinations":[]}
    """
    Then we get error 400
    """
    {"_issues": {"destinations": {"minlength": 1}}, "_status": "ERR"}
    """

  @auth
  Scenario: Creating a Subscriber should fail when Mandatory properties are not passed for destinations
    Given empty "subscribers"
    When we post to "/subscribers"
    """
    {
      "name":"News1", "subscriber_type": "digital","media_type":"media", "sequence_num_settings":{"min" : 1, "max" : 10},
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
      "name":"News1", "subscriber_type": "digital","media_type":"media", "sequence_num_settings":{"min" : 0, "max" : 10}, "email": "test@test.com",
      "destinations":[{"name":"destination1","format": "nitf", "delivery_type":"FTP","config":{"ip":"144.122.244.55","password":"xyz"}}]
    }
    """
    Then we get error 400
    """
    {"_issues": {"sequence_num_settings.min": 1}, "_message": "Value of Minimum in Sequence Number Settings should be greater than 0"}
    """

  @auth
  @notification
  Scenario: Update critical errors for subscriber 1
    Given empty "subscribers"
    When we post to "/subscribers" with success
    """
    {
      "name":"News1","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
      "destinations":[{"name":"destination1","format": "nitf", "delivery_type":"FTP","config":{"ip":"144.122.244.55","password":"xyz"}}]
    }
    """
    When we patch "/subscribers/#subscribers._id#"
    """
    {"critical_errors":{"6000":true, "6001":true}}
    """
    Then we get updated response
    """
    {"critical_errors":{"6000":true, "6001":true}}
    """

  @auth
  @vocabulary
  @notification
  Scenario: Update critical errors for subscriber 2
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "anpa_category", "operator": "in", "value": "4"}]
    """

    Then we get latest
    Given empty "publish_filters"
    When we post to "/publish_filters" with success
    """
    [{"publish_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer-only"}]
    """

    Then we get latest
    Given empty "subscribers"
    When we post to "/subscribers" with success
    """
    {
      "name":"News1","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
      "destinations":[{"name":"destination1","format": "nitf", "delivery_type":"FTP","config":{"ip":"144.122.244.55","password":"xyz"}}]
    }
    """
    When we patch "/subscribers/#subscribers._id#"
    """
    {"global_filters":{"#publish_filters._id#":true}}
    """
    Then we get updated response
    """
    {"global_filters":{"#publish_filters._id#":true}}
    """
