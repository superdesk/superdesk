Feature: Routing Scheme and Routing Rules

    @auth
    Scenario: List empty routing schemes
      Given empty "routing_schemes"
      When we get "/routing_schemes"
      Then we get list with 0 items

    @auth @vocabulary
    Scenario: Create a valid Routing Scheme
      Given empty "desks"
      And we have "/filter_conditions" with "FCOND_ID" and success
      """
      [{
          "name": "Sports Content",
          "field": "subject",
          "operator": "in",
          "value": "04000000"
      }]
      """
      And we have "/content_filters" with "FILTER_ID" and success
      """
      [{
          "name": "Sports Content",
          "content_filter": [
              {
                  "expression": {
                      "fc": ["#FCOND_ID#"]
                  }
              }
          ]
      }]
      """

      When we post to "/desks"
      """
      {"name": "Sports", "members": [{"user": "#CONTEXT_USER_ID#"}]}
      """
      And we post to "/routing_schemes"
      """
      [
        {
          "name": "routing rule scheme 1",
          "rules": [
            {
              "name": "Sports Rule",
              "filter": "#FILTER_ID#",
              "actions": {
                "fetch": [
                            {"desk": "#desks._id#",
                              "stage": "#desks.incoming_stage#",
                              "macro": "transform"}]
              }
            }
          ]
        }
      ]
      """
      Then we get response code 201
      When we get "/routing_schemes"
      Then we get existing resource
      """
      {
        "_items":
          [
            {
              "name": "routing rule scheme 1",
              "rules": [
                {
                  "name": "Sports Rule",
                  "filter": "#FILTER_ID#",
                  "actions": {
                    "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "macro": "transform"}]
                  }
                }
              ]
            }
          ]
      }
      """

    @auth @vocabulary
    Scenario: A Routing Scheme must have a unique name
      Given empty "desks"
      And we have "/filter_conditions" with "FCOND_ID" and success
      """
      [{
          "name": "Sports Content",
          "field": "subject",
          "operator": "in",
          "value": "04000000"
      }]
      """
      And we have "/content_filters" with "FILTER_ID" and success
      """
      [{
          "name": "Sports Content",
          "content_filter": [
              {
                  "expression": {
                      "fc": ["#FCOND_ID#"]
                  }
              }
          ]
      }]
      """
      When we post to "/desks"
      """
      {"name": "Sports", "members": [{"user": "#CONTEXT_USER_ID#"}]}
      """
      And we post to "/routing_schemes"
      """
      [
        {
          "name": "routing rule scheme 1",
          "rules": [
            {
              "name": "Sports Rule",
              "filter": "#FILTER_ID#",
              "actions": {
                "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
              }
            }
          ]
        }
      ]
      """
      Then we get response code 201
      When we post to "/routing_schemes"
      """
      [
        {
          "name": "ROUTING rule scheme 1",
          "rules": [
            {
              "name": "Sports Rule",
              "filter": "#FILTER_ID#",
              "actions": {
                "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
              }
            }
          ]
        }
      ]
      """
      Then we get response code 400

    @auth
    Scenario: Create an invalid Routing Scheme with no rules
      Given empty "routing_schemes"
      When we post to "/routing_schemes"
      """
      [
        {
          "name": "routing rule scheme 1",
          "rules": []
        }
      ]
      """
      Then we get response code 400

    @auth @vocabulary
    Scenario: Create an invalid Routing Scheme with rules having same name
      Given empty "desks"
      And we have "/filter_conditions" with "FCOND_1_ID" and success
      """
      [{
          "name": "Sports Content",
          "field": "subject",
          "operator": "in",
          "value": "04000000"
      }]
      """
      And we have "/filter_conditions" with "FCOND_2_ID" and success
      """
      [{
          "name": "Non-Sports Content",
          "field": "subject",
          "operator": "nin",
          "value": "04000000"
      }]
      """
      And we have "/content_filters" with "FILTER_1_ID" and success
      """
      [{
          "name": "Sports Content",
          "content_filter": [
              {
                  "expression": {
                      "fc": ["#FCOND_1_ID#"]
                  }
              }
          ]
      }]
      """
      And we have "/content_filters" with "FILTER_2_ID" and success
      """
      [{
          "name": "Non-Sports Content",
          "content_filter": [
              {
                  "expression": {
                      "fc": ["#FCOND_2_ID#"]
                  }
              }
          ]
      }]
      """

      When we post to "/desks"
      """
      {"name": "Sports", "members": [{"user": "#CONTEXT_USER_ID#"}]}
      """
      And we post to "/routing_schemes"
      """
      [
        {
          "name": "routing rule scheme 1",
          "rules": [
            {
              "name": "Content Rule",
              "filter": "#FILTER_1_ID#",
              "actions": {
                "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
              }
            },
            {
              "name": "Content Rule",
              "filter": "#FILTER_2_ID#",
              "actions": {
                "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
              }
            }
          ]
        }
      ]
      """
      Then we get response code 400


    @auth @test
    Scenario: Create a valid Routing Scheme with an empty filter
      Given empty "desks"

      When we post to "/desks"
      """
      {"name": "Sports", "members": [{"user": "#CONTEXT_USER_ID#"}]}
      """
      When we post to "/routing_schemes"
      """
      [
        {
          "name": "routing rule scheme 1",
          "rules": [{
            "name": "Sports Rule",
            "filter": null,
            "actions": {
                "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
            }
          }]
        }
      ]
      """
      Then we get response code 201

    @auth @vocabulary
    Scenario: Create an invalid Routing Scheme with a empty actions
      Given we have "/filter_conditions" with "FCOND_ID" and success
      """
      [{
          "name": "Sports Content",
          "field": "subject",
          "operator": "in",
          "value": "04000000"
      }]
      """
      And we have "/content_filters" with "FILTER_ID" and success
      """
      [{
          "name": "Sports Content",
          "content_filter": [
              {
                  "expression": {
                      "fc": ["#FCOND_ID#"]
                  }
              }
          ]
      }]
      """
      And empty "routing_schemes"

      When we post to "/routing_schemes"
      """
      [
        {
          "name": "routing rule scheme 1",
          "rules": [{
            "name": "Sports Rule",
            "filter": "#FILTER_ID#",
            "actions": {}
          }]
        }
      ]
      """
      Then we get response code 400


    @auth @vocabulary
    Scenario: Create an invalid Routing Scheme with an invalid schedule
      Given empty "routing_schemes"
      Given empty "desks"
      Given we have "/filter_conditions" with "FCOND_ID" and success
      """
      [{
          "name": "Sports Content",
          "field": "subject",
          "operator": "in",
          "value": "04000000"
      }]
      """
      And we have "/content_filters" with "FILTER_ID" and success
      """
      [{
          "name": "Sports Content",
          "content_filter": [
              {
                  "expression": {
                      "fc": ["#FCOND_ID#"]
                  }
              }
          ]
      }]
      """

      When we post to "/desks"
      """
      {"name": "Sports", "members": [{"user": "#CONTEXT_USER_ID#"}]}
      """
      Then we get response code 201
      When we post to "/routing_schemes"
      """
      [
        {
          "name": "routing rule scheme 1",
          "rules": [
            {
              "name": "Sports Rule",
              "filter": "#FILTER_ID#",
              "actions": {
                "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
              },
              "schedule": {
                "day_of_week": ["ddd", "TUE"]
              }
            }
          ]
        }
      ]
      """
      Then we get response code 400

      When we post to "/routing_schemes"
      """
      [
        {
          "name": "routing rule scheme 1",
          "rules": [
            {
              "name": "Sports Rule",
              "filter": "#FILTER_ID#",
              "actions": {
                "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
              },
              "schedule": {
                "day_of_week": ["FRI", "TUE"],
                "hour_of_day_from": "ddd",
                "hour_of_day_to": "0040"
              }
            }
          ]
        }
      ]
      """
      Then we get response code 400

      When we post to "/routing_schemes"
      """
      [
        {
          "name": "routing rule scheme 1",
          "rules": [
            {
              "name": "Sports Rule",
              "filter": "#FILTER_ID#",
              "actions": {
                "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
              },
              "schedule": {
                "day_of_week": ["FRI", "TUE"],
                "hour_of_day_from": "",
                "hour_of_day_to": "0040"
              }
            }
          ]
        }
      ]
      """
      Then we get response code 400

      When we post to "/routing_schemes"
      """
      [
        {
          "name": "routing rule scheme 1",
          "rules": [
            {
              "name": "Sports Rule",
              "filter": "#FILTER_ID#",
              "actions": {
                "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
              },
              "schedule": {
                "day_of_week": ["FRI", "TUE"],
                "hour_of_day_from": "0600",
                "hour_of_day_to": "0400"
              }
            }
          ]
        }
      ]
      """
      Then we get response code 400

      When we post to "/routing_schemes"
      """
      [
        {
          "name": "routing rule scheme 1",
          "rules": [
            {
              "name": "Sports Rule",
              "filter": "#FILTER_ID#",
              "actions": {
                "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
              },
              "schedule": {
                "day_of_week": ["FRI", "TUE"],
                "hour_of_day_from": "0400",
                "hour_of_day_to": "0600",
                "time_zone": "Timezone/Invalid"
              }
            }
          ]
        }
      ]
      """
      Then we get response code 400

      When we post to "/routing_schemes"
      """
      [
        {
          "name": "routing rule scheme 1",
          "rules": [
            {
              "name": "Sports Rule",
              "filter": "#FILTER_ID#",
              "actions": {
                "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
              },
              "schedule": {
                "day_of_week": ["FRI", "TUE"],
                "hour_of_day_from": "0400",
                "hour_of_day_to": "",
                "time_zone": "Europe/Rome"
              }
            }
          ]
        }
      ]
      """
      Then we get response code 201

    @auth
    Scenario: A user with no privilege to "routing schemes" can't create a Routing Scheme
      Given we login as user "foo" with password "bar" and user type "user"
      """
      {"user_type": "user", "email": "foo.bar@foobar.org"}
      """
      When we post to "/routing_schemes"
      """
      [
        {
          "name": "routing rule scheme 1",
          "rules": [
            {
              "name": "Sports Rule",
              "filter": null,
              "actions": {
                "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
              },
              "schedule": {}
            }
          ]
        }
      ]
      """
      Then we get response code 403

    @auth @vocabulary
    Scenario: Update Routing Scheme
      Given empty "desks"
      And we have "/filter_conditions" with "FCOND_1_ID" and success
      """
      [{
          "name": "Sports Content",
          "field": "subject",
          "operator": "in",
          "value": "04000000"
      }]
      """
      And we have "/filter_conditions" with "FCOND_2_ID" and success
      """
      [{
          "name": "Non-Sports Content",
          "field": "subject",
          "operator": "nin",
          "value": "04000000"
      }]
      """
      And we have "/content_filters" with "FILTER_1_ID" and success
      """
      [{
          "name": "Sports Content",
          "content_filter": [
              {
                  "expression": {
                      "fc": ["#FCOND_1_ID#"]
                  }
              }
          ]
      }]
      """
      And we have "/content_filters" with "FILTER_2_ID" and success
      """
      [{
          "name": "Non-Sports Content",
          "content_filter": [
              {
                  "expression": {
                      "fc": ["#FCOND_2_ID#"]
                  }
              }
          ]
      }]
      """

      When we post to "/desks"
      """
      {"name": "Sports"}
      """
      And we post to "/routing_schemes"
      """
      [
        {
          "name": "routing rule scheme 1",
          "rules": [
            {
              "name": "Sports Rule",
              "filter": "#FILTER_1_ID#",
              "actions": {
                "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
              }
            }
          ]
        }
      ]
      """
      Then we get response code 201
      When we patch "/routing_schemes/#routing_schemes._id#"
      """
      {
        "rules": [
          {
            "name": "Sports Rule",
            "filter": "#FILTER_1_ID#",
            "actions": {
              "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "macro": "transform"}]
            }
          },
          {
            "name": "Non-Sports Rule",
            "filter": "#FILTER_2_ID#",
            "actions": {
              "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
            }
          }
        ]
      }
      """
      Then we get response code 200

    @auth @vocabulary
    Scenario: Delete a Routing Scheme
      Given empty "desks"
      Given we have "/filter_conditions" with "FCOND_ID" and success
      """
      [{
          "name": "Sports Content",
          "field": "subject",
          "operator": "in",
          "value": "04000000"
      }]
      """
      And we have "/content_filters" with "FILTER_ID" and success
      """
      [{
          "name": "Sports Content",
          "content_filter": [
              {
                  "expression": {
                      "fc": ["#FCOND_ID#"]
                  }
              }
          ]
      }]
      """

      When we post to "/desks"
      """
      {"name": "Sports"}
      """
      And we post to "/routing_schemes"
      """
      [
        {
          "name": "routing rule scheme 1",
          "rules": [
            {
              "name": "Sports Rule",
              "filter": "#FILTER_ID#",
              "actions": {
                "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
              }
            }
          ]
        }
      ]
      """
      Then we get response code 201
      When we delete "/routing_schemes/#routing_schemes._id#"
      Then we get response code 204


    @auth
    Scenario: Delete routing scheme when in use
      Given empty "desks"

      When we post to "/desks"
        """
        {"name": "Sports"}
        """
      And we post to "/routing_schemes"
        """
        [
          {
            "name": "routing rule scheme 1",
            "rules": [
              {
                "name": "Sports Rule",
                "filter": null,
                "actions": {
                    "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
                    }
              }
            ]
          }
        ]
        """
      And we post to "ingest_providers"
        """
        [{"name": "test", "type": "reuters", "source": "reuters", "routing_scheme": "#routing_schemes._id#"}]
        """
      When we delete "/routing_schemes/#routing_schemes._id#"
      Then we get response code 403

    @auth
    Scenario: Cannot delete desk when routing schemes are associated
      Given empty "desks"

      When we post to "/desks"
      """
      {"name": "Sports"}
      """
      And we post to "/routing_schemes"
      """
      [
        {
          "name": "routing rule scheme 1",
          "rules": [
            {
              "name": "Sports Rule",
              "filter": null,
              "actions": {
                  "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
                  }
            }
          ]
        }
      ]
      """
      And we delete "/desks/#desks._id#"
      Then we get error 412
      """
      {"_message": "Cannot delete desk as routing scheme(s) are associated with the desk"}
      """
