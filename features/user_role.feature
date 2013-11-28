@wip
Feature: User Role Resource

    @auth
    Scenario: List empty user roles
        Given empty "user_roles"
        When we get "/user_roles"
        Then we get list with 0 items

    @auth
    Scenario: Create a new child role
        Given "user_roles"
            """
            [{"_id": "528de7b03b80a13eefc5e610", "name": "Administrator"}]
            """

        When we post to "/user_roles"
            """
            {"name": "Editor", "child_of": "528de7b03b80a13eefc5e610"}
            """

        And we get "/user_roles"
        Then we get list with 2 items

    @auth
    Scenario: Set permissions for given role
        Given "user_roles"
            """
            [{"name": "Admin"}]
            """

        When we patch it
            """
            {"permissions": [
                {"resource": "ingest", "method": "get"},
                {"resource": "archive", "method": "get"}
            ]}
            """

        And we get it
        Then we get "permissions"

    @auth
    Scenario: Check permissions on read with role
        Given "user_roles"
            """
            [{"name": "User"}]
            """

        And we have "User" role
        When we get "/ingest"
        Then we get response code 401

    @auth
    Scenario: Check permissions on read with role and permissions
        Given "user_roles"
            """
            [{"name": "Editor", "permissions": [
                {"resource": "ingest", "method": "get"}
            ]}]
            """
        And we have "Editor" role
        When we get "/ingest"
        Then we get response code 200
