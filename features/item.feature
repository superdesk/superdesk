@wip
Feature: Item resource

    @auth
    Scenario: List empty items
        Given empty "items"
        When we get "/items"
        Then we get list with 0 items

    @auth
    Scenario: Create item
        Given empty "items"
        When we post to "/items"
            """
            {"headline": "test"}
            """

        Then we get new resource
            """
            {"headline": "text"}
            """

    @auth
    Scenario: Update item
        Given "items"
            """
            {"guid": "testid", "headline": "test"}
            """

        When we patch "/items/testid"
            """
            {"slugline": "TEST"}
            """

        Then we get updated response
