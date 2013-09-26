@wip
Feature: User Resource

    @auth
    Scenario: Create a user
        Given no user
        When we post to "/users"
            """
            {"username": "foo"}
            """

        Then we get new resource
            """
            {"username": "foo"}
            """

    @auth
    Scenario: List users
        Given users
            """
            {"username": "foo"}, {"username": "bar"}
            """

        When we get "/users"
        Then we get list with 2 items
