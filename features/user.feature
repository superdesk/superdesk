Feature: User Resource

    @auth
    Scenario: Create a user
        Given empty "users"
        When we post to "/users"
            """
            {"username": "foo", "password": "barbar", "email": "foo@bar.com"}
            """

        Then we get new resource
            """
            {"username": "foo", "display_name": "foo", "email": "foo@bar.com"}
            """
        And we get no "password"

    @auth
    Scenario: Test email validation
        Given empty "users"
        When we post to "/users"
            """
            {"username": "foo", "password": "barbar", "email": "invalid email"}
            """

        Then we get error 200
            """
            {"_status": "ERR", "_issues": {"email": "must be of Email type"}}
            """

    @auth
    Scenario: Test phone validation
        Given empty "users"
        When we post to "/users"
            """
            {"username": "foo", "password": "barbar", "phone": "0123"}
            """

        Then we get error 200
            """
            {"_issues": {"phone": "must be of Phone Number type"}, "_status": "ERR"}
            """

    @auth
    Scenario: List users
        Given "users"
            """
            [{"username": "foo"}, {"username": "bar"}]
            """

        When we get "/users"
        Then we get list with 2 items

    @auth
    Scenario: Fetch single user
        Given "users"
            """
            [{"username": "foo", "first_name": "Foo", "last_name": "Bar"}]
            """

        When we get "/users/foo"
        Then we get existing resource
            """
            {"username": "foo", "first_name": "Foo", "last_name": "Bar", "display_name": "Foo Bar", "_created": "", "_updated": "", "_id": ""}
            """
        And we get no "password"

    @auth
    Scenario: Delete user
        Given "users"
            """
            [{"username": "foo"}]
            """

        When we delete "/users/foo"
        Then we get response code 200

    @auth
    Scenario: Update user
        Given "users"
            """
            [{"username": "foo"}]
            """

        When we patch "/users/foo"
            """
            {"first_name": "Foo"}
            """

        Then we get updated response
