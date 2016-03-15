Feature: Example test

    @auth
    Scenario: Empty groups list
        Given empty "groups"
        When we get "/groups"
        Then we get list with 0 items
