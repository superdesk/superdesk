Feature: Authentication

    Scenario: Authenticate existing user
        Given "users"
            """
            [{"username": "foo", "password": "bar"}]
            """

        When we post to auth
            """
            {"username": "foo", "password": "bar"}
            """

        Then we get "token"
        And we get "user"

    Scenario: Authenticate with wrong password returns error
        Given "users"
            """
            [{"username": "foo", "password": "bar"}]
            """

        When we post to auth
            """
            {"username": "foo", "password": "xyz"}
            """

        Then we get response code 403

    Scenario: Authenticate with non existing username
        Given "users"
            """
            [{"username": "foo", "password": "bar"}]
            """

        When we post to auth
            """
            {"username": "x", "password": "y"}
            """

        Then we get response code 404

    Scenario: Fetch resources without auth token
        When we get "/"
        Then we get response code 401

    @auth
    Scenario: Get auth info with auth token
        When we get "/"
        Then we get response code 200
