Feature: Privilege

    @auth
    Scenario: Get list of all privileges
        When we get "/privileges"
        Then we get list with 10+ items
            """
            {"_items": [{"name": "ingest"}, {"name": "archive"}]}
            """

    @auth
    Scenario: Post to a resource without required privilege
        Given we have "user" as type of user
        When we post to "/users"
            """
            {"username": "foo"}
            """
        Then we get response code 403

    @auth
    Scenario: Post to a resource having role with required privilege
        Given "roles"
            """
            [{"name": "Manager", "privileges": {"users": 1}}]
            """
        Given we have "Manager" role
        Given we have "user" as type of user
        When we post to "/users"
            """
            {"username": "foo", "email": "foo@example.com", "sign_off": "abc"}
            """
        Then we get response code 201
