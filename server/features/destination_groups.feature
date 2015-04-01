Feature:Destination Groups

  @auth
  Scenario: Add Destination Group
    Given empty "destination_groups"
    When we get "/destination_groups"
    Then we get list with 0 items
    When we post to "/destination_groups"
    """
    {
      "name":"test", "description": "new stuff",
      "destination_groups": [], "output_channels": []
    }
    """
    And we get "/destination_groups"
    Then we get list with 1 items
    """
    {
      "_items":
        [
          {
            "name":"test", "description": "new stuff",
            "destination_groups": [], "output_channels": []
          }
        ]
    }
    """

  @auth
  Scenario: Update Destination Group
    Given empty "destination_groups"
    When we get "/destination_groups"
    Then we get list with 0 items
    When we post to "/destination_groups" with "destgroup1" and success
    """
    [
      {
        "name":"Group 1", "description": "new stuff",
        "destination_groups": [], "output_channels": []
      }
    ]
    """
    Then we get existing resource
    """
      {
        "_id":"#destgroup1#",
        "name":"Group 1", "description": "new stuff",
        "destination_groups": [], "output_channels": []
      }
    """
    When we post to "/output_channels" with "channel1" and success
    """
    [{"name":"Group 2", "description": "new stuff"}]
    """
    Then we get existing resource
    """
    {"_id":"#channel1#", "name":"Group 2", "description": "new stuff"}
    """
    When we post to "/destination_groups" with "destgroup2" and success
    """
    [{
      "name":"Group 2", "description": "new stuff",
      "destination_groups": [{"group":"#destgroup1#"}],
      "output_channels": [{"channel":"#channel1#", "selector_codes": ["PXX", "XYZ"]}]
    }]
    """
    Then we get existing resource
    """
    {
      "name":"Group 2", "description": "new stuff",
      "destination_groups": [{"group":"#destgroup1#"}],
      "output_channels": [{"channel":"#channel1#", "selector_codes": ["PXX", "XYZ"]}]
    }
    """
    When we patch "/destination_groups/#destgroup2#"
    """
    {
      "name":"testing", "description": "stuff testing"
    }
    """
    Then we get updated response
    """
    {
      "name":"testing", "description": "stuff testing"
    }
    """

  @auth
  Scenario: Delete Destination Group
    Given "destination_groups"
    """
    [
      {
        "name":"Group 1", "description": "new stuff",
        "destination_groups": [], "output_channels": []
      }
    ]
    """
    When we delete "/destination_groups/#destination_groups._id#"
    Then we get deleted response


  @auth
  Scenario: Failure to delete Destination Group referenced by another Destination Group
    Given empty "destination_groups"
    When we get "/destination_groups"
    Then we get list with 0 items
    When we post to "/destination_groups" with "destgroup1" and success
    """
    [
      {
        "name":"Group 1", "description": "new stuff",
        "destination_groups": [], "output_channels": []
      }
    ]
    """
    Then we get existing resource
    """
      {
        "_id":"#destgroup1#",
        "name":"Group 1", "description": "new stuff",
        "destination_groups": [], "output_channels": []
      }
    """
    When we post to "/destination_groups" with "destgroup2" and success
    """
    [{
      "name":"Group 2", "description": "new stuff",
      "destination_groups": [{"group":"#destgroup1#"}],
      "output_channels": []
    }]
    """
    Then we get existing resource
    """
    {
      "name":"Group 2", "description": "new stuff",
      "destination_groups": [{"group":"#destgroup1#"}],
      "output_channels": []
    }
    """
    When we delete "/destination_groups/#destgroup1#"
    Then we get error 412
    """
    {"_message":"Destination Group is referenced by other Destination Group/s.", "_status": "ERR"}
    """

  @auth
  Scenario: Failure to have self referenced Destination Group
    Given empty "destination_groups"
    When we get "/destination_groups"
    Then we get list with 0 items
    When we post to "/destination_groups" with "destgroup1" and success
    """
    [
      {
        "name":"Group 1", "description": "new stuff",
        "destination_groups": [], "output_channels": []
      }
    ]
    """
    Then we get existing resource
    """
      {
        "_id":"#destgroup1#",
        "name":"Group 1", "description": "new stuff",
        "destination_groups": [], "output_channels": []
      }
    """
    When we post to "/destination_groups" with "destgroup2" and success
    """
    [{
      "name":"Group 2", "description": "new stuff",
      "destination_groups": [{"group":"#destgroup1#"}],
      "output_channels": []
    }]
    """
    Then we get existing resource
    """
    {
      "name":"Group 2", "description": "new stuff",
      "destination_groups": [{"group":"#destgroup1#"}],
      "output_channels": []
    }
    """
    When we post to "/destination_groups" with "destgroup3" and success
    """
    [{
      "name":"Group 3", "description": "new stuff",
      "destination_groups": [{"group":"#destgroup2#"}],
      "output_channels": []
    }]
    """
    Then we get existing resource
    """
    {
      "name":"Group 3", "description": "new stuff",
      "destination_groups": [{"group":"#destgroup2#"}],
      "output_channels": []
    }
    """
    When we patch "/destination_groups/#destgroup1#"
    """
    {
      "name":"Group 1 testing",
      "destination_groups": [{"group":"#destgroup2#"}]
    }
    """
    Then we get error 400
    """
    {"_issues": {"validator exception":"400: Circular dependency in Destination Group."}}
    """
    When we patch "/destination_groups/#destgroup2#"
    """
    {
      "name":"Group 1 testing",
      "destination_groups": [{"group":"#destgroup1#"}, {"group": "#destgroup3#"}]
    }
    """
    Then we get error 400
    """
    {"_issues": {"validator exception":"400: Circular dependency in Destination Group."}}
    """

  @auth
  Scenario: Failure to delete Destination Group referenced by routing scheme.
    Given empty "destination_groups"
    When we get "/destination_groups"
    Then we get list with 0 items
    When we post to "/destination_groups" with "destgroup1" and success
    """
    [
      {
        "name":"Group 1", "description": "new stuff",
        "destination_groups": [], "output_channels": []
      }
    ]
    """
    Then we get response code 201
    When we post to "/destination_groups" with "destgroup2" and success
    """
    [{
      "name":"Group 2", "description": "new stuff",
      "destination_groups": [],
      "output_channels": []
    }]
    """
    Then we get response code 201
    When we post to "/desks" with "sportsdesk" and success
    """
      [{
        "name": "Sports Desk", "members": [{"user": "#CONTEXT_USER_ID#"}]
      }]
    """
    Then we get response code 201
    When we post to "/routing_schemes"
    """
     {
        "name": "routing rule scheme 1",
        "rules": [
          {
            "name": "Sports Rule",
            "filter": {
              "subject": [{"qcode": "15000000"}]
            },
            "actions": {
              "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#",
                        "destination_groups": [{"group": "#destgroup1#"}]}],
              "publish": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#",
                        "destination_groups": [{"group": "#destgroup2#"}]}],
              "exit": false
            }
          }
        ]
      }
    """
    Then we get response code 201
    When we delete "/destination_groups/#destgroup1#"
    Then we get error 412
    """
    {"_message":"Destination Group is referenced by Routing Scheme/s.", "_status": "ERR"}
    """
    When we delete "/destination_groups/#destgroup2#"
    Then we get error 412
    """
    {"_message":"Destination Group is referenced by Routing Scheme/s.", "_status": "ERR"}
    """

  @auth
  Scenario: Failure to delete Destination Group referenced by content.
    Given empty "destination_groups"
    When we get "/destination_groups"
    Then we get list with 0 items
    When we post to "/destination_groups" with "destgroup1" and success
    """
    [
      {
        "name":"Group 1", "description": "new stuff",
        "destination_groups": [], "output_channels": []
      }
    ]
    """
    When we post to "/desks" with "sportsdesk" and success
    """
      [{
        "name": "Sports Desk", "members": [{"user": "#CONTEXT_USER_ID#"}]
      }]
    """
    Then we get response code 201
    Given "archive"
    """
    [
      {
        "guid": "tag:example.com,0000:newsml_BRE9A605",
        "destination_groups": [
          {"group": "#destgroup1#"}
        ], "task" : {"desk": "#sportsdesk#", "user": "#CONTEXT_USER_ID#"}
      }
    ]
    """

    When we get "/archive/tag:example.com,0000:newsml_BRE9A605"
    Then we get existing resource
    """
    {"guid": "tag:example.com,0000:newsml_BRE9A605", "state": "draft",
        "destination_groups": [
          {"group": "#destgroup1#"}
        ]
    }
    """
    When we delete "/destination_groups/#destgroup1#"
    Then we get error 412
    """
    {"_message":"Destination Group is referenced by items.", "_status": "ERR"}
    """