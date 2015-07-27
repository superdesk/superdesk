Feature: Routing Scheme and Routing Rules

    @auth
    Scenario: List empty routing schemes
      Given empty "routing_schemes"
      When we get "/routing_schemes"
      Then we get list with 0 items

    @auth
    Scenario: Create a valid Routing Scheme
      Given empty "desks"
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
              "filter": {
                "category": [{"name": "Overseas Sport", "qcode": "S"}]
              },
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
                  "filter": {
                    "category": [{"name": "Overseas Sport", "qcode": "S"}]
                  },
                  "actions": {
                    "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "macro": "transform"}]
                  }
                }
              ]
            }
          ]
      }
      """

    @auth
    Scenario: A Routing Scheme must have a unique name
      Given empty "desks"
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
              "filter": {
                "category": [{"name": "Overseas Sport", "qcode": "S"}]
              },
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
              "filter": {
                "category": [{"name": "Overseas Sport", "qcode": "S"}]
              },
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

    @auth
    Scenario: Create an invalid Routing Scheme with rules having same name
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
          "rules": [
            {
              "name": "Sports Rule",
              "filter": {
                "category": [{"name": "Australian News", "qcode": "A"}]
              },
              "actions": {
                "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
              }
            },
            {
              "name": "Sports Rule",
              "filter": {
                "category": [{"name": "Overseas Sport", "qcode": "S"}]
              },
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
    Scenario: Create an valid Routing Scheme with an empty filter
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
            "filter": {},
            "actions": {
                "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
            }
          }]
        }
      ]
      """
      Then we get response code 201

    @auth
    Scenario: Create an invalid Routing Scheme with a empty actions
      Given empty "routing_schemes"
      When we post to "/routing_schemes"
      """
      [
        {
          "name": "routing rule scheme 1",
          "rules": [{
            "name": "Sports Rule",
            "filter": {
              "category": [{"name": "Overseas Sport", "qcode": "S"}]
            },
            "actions": {}
          }]
        }
      ]
      """
      Then we get response code 400


    @auth
    Scenario: Create an invalid Routing Scheme with an invalid schedule
      Given empty "routing_schemes"
      Given empty "desks"
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
              "filter": {
                "category": [{"name": "Overseas Sport", "qcode": "S"}]
              },
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
              "filter": {
                "category": [{"name": "Overseas Sport", "qcode": "S"}]
              },
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
              "filter": {
                "category": [{"name": "Overseas Sport", "qcode": "S"}]
              },
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
              "filter": {
                "category": [{"name": "Overseas Sport", "qcode": "S"}]
              },
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
              "filter": {
                "category": [{"name": "Overseas Sport", "qcode": "S"}]
              },
              "actions": {
                "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
              },
              "schedule": {
                "day_of_week": ["FRI", "TUE"],
                "hour_of_day_from": "0400",
                "hour_of_day_to": "0600"
              }
            }
          ]
        }
      ]
      """
      Then we get response code 201

    @auth
    Scenario: Create an invalid Routing Scheme with a empty schedule
      Given empty "desks"
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
              "filter": {
                "category": [{"name": "Overseas Sport", "qcode": "S"}]
              },
              "actions": {
                "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
              },
              "schedule": {}
            }
          ]
        }
      ]
      """
      Then we get response code 400

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
              "filter": {
                "category": [{"name": "Overseas Sport", "qcode": "S"}]
              },
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

    @auth
    Scenario: Update Routing Scheme
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
              "filter": {
                "category": [{"name": "Overseas Sport", "qcode": "S"}]
              },
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
            "name": "Australian News Rule",
            "filter": {
              "category": [{"name": "Australian News", "qcode": "A"}]
            },
            "actions": {
              "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "macro": "transform"}]
            }
          },
          {
            "name": "Sports Rule",
            "filter": {
              "category": [{"name": "Overseas Sport", "qcode": "S"}]
            },
            "actions": {
              "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
            }
          }
        ]
      }
      """
      Then we get response code 200

    @auth
    Scenario: Delete a Routing Scheme
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
              "filter": {
                "category": [{"name": "Overseas Sport", "qcode": "S"}]
              },
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
                "filter": {
                    "category": [{"name": "Overseas Sport", "qcode": "S"}]
                    },
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
              "filter": {
                  "category": [{"name": "Overseas Sport", "qcode": "S"}]
                  },
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
