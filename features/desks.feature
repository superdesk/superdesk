Feature: Desks

    @auth
    Scenario: Empty desks list
        Given empty "desks"
        When we get "/desks"
        Then we get list with 0 items

    @auth
    Scenario: Create new desk
        Given empty "desks"
        When we post to "/desks"
            """
            {"name": "Sports Desk"}
            """

        And we get "/desks"
        Then we get list with 1 items
            """
            {"name": "Sports Desk"}
            """

