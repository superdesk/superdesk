Feature: Role Resource

    @auth
    Scenario: List empty user roles
        Given empty "roles"
        When we get "/roles"
        Then we get list with 0 items

    @auth
    Scenario: Set privileges to a given role
        Given "roles"
            """
            [{"name": "Admin"}]
            """

        When we patch given
            """
            {"privileges": {"ingest":  1, "archive": 1}}
            """

        And we get given
        Then we get "privileges"

    @auth
    @notification
    Scenario: Revoke privileges from a given role
        Given "roles"
            """
            [{"name": "Admin", "privileges": {"ingest":  1, "archive": 1}}]
            """

        When we patch given
            """
            {"privileges": {"ingest":  0}}
            """
        Then we get updated response
        Then we get notifications
            """
            [{"event": "role_privileges_revoked", "extra": {"updated": 1, "role_id": "#roles._id#"}}]
            """

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
            [{"name": "Editor", "privileges": {"ingest": 1}}]
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
            [{"name": "Pool Subs", "privileges": {"desks": 1}}]
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
            [{"name": "big"}]
            """
        Then we get response code 400

    @auth
    Scenario: Can not delete default role
        Given "roles"
            """
            [{"name": "This is a default role", "is_default": true }]
            """

        When we delete "/roles/#roles._id#"

        Then we get response code 403

    @auth
    Scenario: Only one default
        Given "roles"
            """
            [{"name": "A", "is_default": true }]
            """

        When we post to "/roles"
            """
            [{"name": "B", "is_default": true }]
            """
        When we get "/roles/#roles._id#"
        Then we get existing resource
            """
            {"is_default": true}
            """

    @auth
    Scenario: Cannot delete a role that has users in it
        Given "roles"
            """
            [{"name": "A" }]
            """
        Given "users"
            """
            [{"username": "foo", "first_name": "Foo", "last_name": "Bar", "email": "foo@bar.org", "is_active": true, "role": "#roles._id#"}]
            """
        When we delete "/roles/#roles._id#"
        Then we get response code 403

    @auth
    @notification
    Scenario: Change user role
        Given "roles"
            """
            [{"name": "A" }]
            """
        Given "users"
            """
            [{"username": "foo", "first_name": "Foo", "last_name": "Bar", "email": "foo@bar.org", "is_active": true, "role": "#roles._id#"}]
            """
        When we post to "/roles"
            """
            [{"name": "B" }]
            """
        And we patch "/users/foo"
            """
            {"role": "#roles._id#"}
            """
        Then we get updated response
        Then we get notifications
            """
            [{"event": "user_role_changed", "extra": {"updated": 1, "user_id": "#users._id#"}}]
            """

