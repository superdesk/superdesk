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
        And we get no "password"


    Scenario: Reset password existing user
        Given "users"
        """
        [{"username": "foo", "password": "bar", "email": "foo@bar.org"}]
        """

        When we post to reset_password we get email with token
        And we reset password for user

    Scenario: Authenticate with wrong password returns error
        Given "users"
            """
            [{"username": "foo", "password": "bar"}]
            """

        When we post to auth
            """
            {"username": "foo", "password": "xyz"}
            """

        Then we get error 400
            """
            {"_status": "ERR", "_issues": {"credentials": 1}}
            """

    Scenario: Authenticate with non existing username
        Given "users"
            """
            [{"username": "foo", "password": "bar"}]
            """

        When we post to auth
            """
            {"username": "x", "password": "y"}
            """

        Then we get error 400
            """
            {"_status": "ERR", "_issues": {"credentials": 1}}
            """

    Scenario: Fetch resources without auth token
        When we get "/"
        Then we get response code 200

    Scenario: Fetch users without auth token
        When we get "/users"
        Then we get error 401
            """
            {"_status": "ERR", "_issues": {"auth": 1}}
            """

        And we get "Access-Control-Allow-Origin" header
