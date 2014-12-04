Feature: Rule Sets Resource

    @auth
    Scenario: List empty rule_sets
        Given empty "rule_sets"
        When we get "/rule_sets"
        Then we get list with 0 items


    @auth
    Scenario: List rule_sets
          When we post to "/rule_sets"
          """
          [
            {
              "name": "set name",
              "rules": [
                {"old": "x", "new": "X"}
              ]
            }
          ]
          """
          Then we get response code 201
          When we get "/rule_sets/"
          Then we get existing resource
          """
          {
            "_items":
              [{
                "name": "set name",
                "rules": [
                  {"old": "x", "new": "X"}
                ]
              }]
          }
          """

    @auth
    Scenario: Delete rule_sets
        Given "rule_sets"
          """
          [
            {
              "name": "set name",
              "rules": [
                {"old": "x", "new": "X"}
              ]
            }
          ]
          """
        When we delete "/roles/#RULE_SETID#"

        Then we get response code 200