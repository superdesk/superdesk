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
        Then we get response code 200

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
    Scenario: User has always permissions to read himself
        Given "roles"
            """
            [{"name": "Subscriber"}]
            """
        And we have "Subscriber" role
        And we have "user" as type of user
        When we get user profile
        Then we get response code 200


    @auth
    Scenario: Inherit permissions from extended roles
        Given "roles"
            """
            [
                {"name": "Journalist", "permissions": {"ingest": {"read": 1}}},
                {"name": "Editor"}
            ]
            """

        And role "Editor" extends "Journalist"
        And we have "Editor" role
        When we get "/ingest"
        Then we get response code 200

    @auth
    Scenario: All users can read everything
        Given we have "user" as type of user
        When we get "/ingest"
        Then we get response code 200

    @auth
    Scenario: Users cannot write to users and roles
        Given we have "user" as type of user
        When we post to "/roles"
            """
            {"name": "Sub Editor"}
            """
        Then we get response code 403

    @auth
    Scenario: Administrators can write to users and roles
        Given we have "administrator" as type of user
        When we post to "/roles"
            """
            {"name": "Sub Editor"}
            """
        Then we get response code 201

    @auth
    Scenario: Users can write to resources if they have permission
        Given "roles"
            """
            [{"name": "Pool Subs", "permissions": {"desks": {"write": 1}}}]
            """
        And we have "Pool Subs" role
        And we have "user" as type of user
        When we post to "/desks"
            """
            {"name": "Sub Editing Desk"}
            """
        Then we get response code 201

    @auth
    Scenario: Users cannot write to resources if they don't have permission
        Given "roles"
            """
            [{"name": "Producers"}]
            """
        And we have "Producers" role
        And we have "user" as type of user
        When we post to "/desks"
            """
            {"name": "Sub Editing Desk"}
            """
        Then we get response code 403

    @auth
    Scenario: Role names are unique case insensitive
        Given "roles"
            """
            [{"name": "BIG"}]
            """
        When we post to "/roles"
            """
            {"name": "big"}
            """
        Then we get response code 400