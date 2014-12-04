Feature: Rule Sets Resource

    @auth
    Scenario: List empty user rule_sets
        Given empty "rule_sets"
        When we get "/rule_sets"
        Then we get list with 0 items
