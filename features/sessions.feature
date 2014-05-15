Feature: Sessions

    @auth
    Scenario: See who is online
        When we get "/sessions"
        Then we get list with 1 items
            """
            {"user": {"username": true, "_id": true}}
            """
