Feature: Role Resource

    @auth
    Scenario: List empty user roles
        Given empty "roles"
        When we get "/roles"
        Then we get list with 0 items

    @auth
    Scenario: Create a new child role
        Given "roles"
            """
            [{"_id": "528de7b03b80a13eefc5e610", "name": "Administrator"}]
            """

        When we post to "/roles"
            """
            {"name": "Editor", "extends": "528de7b03b80a13eefc5e610"}
            """

        And we get "/roles"
        Then we get list with 2 items

    @auth
    Scenario: Set permissions for given role
        Given "roles"
            """
            [{"name": "Admin"}]
            """

        When we patch given
            """
            {"permissions": {"ingest": {"read": 1}, "archive": {"write": 1}}}
            """

        And we get given
        Then we get "permissions"

    @auth
    Scenario: Check permissions on read with role
        Given "roles"
            """
            [{"name": "Administrator"}]
            """

        And we have "Administrator" role
        When we get "/ingest"
        Then we get response code 401

    @auth
    Scenario: Check permissions on read with role and permissions
        Given "roles"
            """
            [{"name": "Editor", "permissions": {"ingest": {"read": 1}}}]
            """
        And we have "Editor" role
        When we get "/ingest"
        Then we get response code 200

    @auth
    Scenario: User has always permissions to edit himself
        Given "roles"
            """
            [{"name": "Subscriber"}]
            """
        And we have "Subscriber" role
        When we get user profile
        Then we get response code 200

    @auth
    Scenario: Inherit permissions from extended roles
        Given "roles"
            """
            [
                {"name": "Jurnalist", "permissions": {"ingest": {"read": 1}}},
                {"name": "Editor"}
            ]
            """

        And role "Editor" extends "Jurnalist"
        And we have "Editor" role
        When we get "/ingest"
        Then we get response code 200
