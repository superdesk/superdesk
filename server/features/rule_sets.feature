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
        When we delete "/rule_sets/#rule_sets._id#"
        Then we get response code 204

    @auth
    Scenario: Delete rule_sets when in use
      Given "rule_sets"
        """
        [{"name": "set name"}]
        """
      Given "ingest_providers"
        """
        [{"name": "test", "feeding_service": "reuters_http", "feed_parser": "newsml2", "rule_set": "#rule_sets._id#"}]
        """

      When we delete "/rule_sets/#rule_sets._id#"
      Then we get response code 403

    @auth
    Scenario: Patch rule_sets
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
        When we patch "/rule_sets/#rule_sets._id#"
          """
            {
              "rules": [
                {"old": "x", "new": "X"},
                {"old": "y", "new":"yt"}
              ]
            }
          """
        Then we get response code 200
        When we get "/rule_sets/#rule_sets._id#"
        Then we get existing resource
        """
              {
                "name": "set name",
                "rules": [
                  {"old": "x", "new": "X"},
                  {"old": "y", "new":"yt"}
                ]
              }
        """
