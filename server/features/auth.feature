@dbauth
Feature: Authentication

    Scenario: Authenticate existing user
        Given "users"
            """
            [{"username": "foo", "password": "bar", "email": "foo@bar.org", "is_active": true}]
            """

        When we post to auth
            """
            {"username": "foo", "password": "bar"}
            """

        Then we get "token"
        And we get "user"
        And we get no "password"


	Scenario: Change user password with success
        Given "users"
        """
        [{"username": "foo", "password": "bar", "email": "foo@bar.org", "is_active": true}]
        """

        When we post to "/change_user_password" with success
        """
        [{"username": "foo", "old_password": "bar", "new_password": "new"}]
        """
        And we post to auth
            """
            {"username": "foo", "password": "new"}
            """

        Then we get "token"
        And we get "user"
        And we get no "password"


	Scenario: Change user password with wrong old password
        Given "users"
        """
        [{"username": "foo", "password": "bar", "email": "foo@bar.org", "is_active": true}]
        """

        When we post to "/change_user_password"
        """
        [{"username": "foo", "old_password": "wrong", "new_password": "new"}]
        """
        Then we get error 401
        """
        {"_issues": {"credentials": 1}}
        """

	Scenario: Check reset password - expired token
        Given "users"
        """
        [{"username": "foo", "password": "bar", "email": "foo@bar.org", "is_active": true}]
        """

        When we post to reset_password we get email with token
        Then we can check if token is valid
        And we update token to be expired
        Then token is invalid

	Scenario: Reset password existing user
        Given "users"
        """
        [{"username": "foo", "password": "bar", "email": "foo@bar.org", "is_active": true}]
        """

        When we post to reset_password we get email with token
        Then we reset password for user

    Scenario: Reset password disabled user
        Given "users"
        """
        [{"username": "foo", "password": "bar", "email": "foo@bar.org", "is_active": false}]
        """

        When we post to "/reset_user_password"
        """
        [{"email": "foo@bar.org"}]
        """
        Then we get error 403

    @auth
    Scenario: Reset password existing user - disabled after mail is sent
        Given "users"
        """
        [{"username": "foo", "password": "bar", "email": "foo@bar.org", "is_active": true}]
        """

        When we post to reset_password we get email with token
        When we change user status to "enabled but inactive" using "/users/foo"
        """
        {"is_active": false}
        """
        Then we fail to reset password for user

    Scenario: Authenticate with wrong password returns error
        Given "users"
            """
            [{"username": "foo", "password": "bar", "email": "foo@bar.org", "is_active": true}]
            """

        When we post to auth
            """
            {"username": "foo", "password": "xyz"}
            """

        Then we get error 401
            """
            {"_status": "ERR", "_issues": {"credentials": 1}}
            """

    Scenario: Authenticate after user is disabled
        Given "users"
            """
            [{"username": "foo", "password": "bar", "is_active": false, "email": "foo@bar.org"}]
            """

        When we post to auth
            """
            {"username": "foo", "password": "bar"}
            """

        Then we get error 403
            """
            {"_issues": {"is_active": false}, "_message": "", "_status": "ERR"}
            """

    Scenario: Authenticate with non existing username
        Given "users"
            """
            [{"username": "foo", "password": "bar", "email": "foo@bar.org", "is_active": true}]
            """

        When we post to auth
            """
            {"username": "x", "password": "y"}
            """

        Then we get error 401
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

    @auth
    Scenario: user logs in and no etag change
        When we post to "/users"
        """
        {"username": "foo", "password": "barbar", "email": "foo@bar.com", "sign_off": "fubar", "is_active": true}
        """
        Then we get response code 201
        And we get new resource
            """
            {"username": "foo", "email": "foo@bar.com"}
            """

        When we post to "auth"
            """
            {"username": "foo", "password": "barbar"}
            """
        Then we get response code 201

        When we get "/users"
        Then we get list with 2 items
            """
            {"_items": [{"username": "foo", "_etag": "#USERS._etag#"}, {"username": "test_user"}]}
            """

     @auth
     Scenario: user logs out and no etag change
        When we post to "/users"
        """
        {"username": "foo", "password": "barbar", "email": "foo@bar.com", "is_active": true, "sign_off": "foobar"}
        """
        Then we get response code 201
        And we get new resource
            """
            {"username": "foo", "email": "foo@bar.com"}
            """

        When we post to auth
            """
            {"username": "foo", "password": "barbar"}
            """
        When we delete latest
        Then we get response code 204

        When we post to auth
            """
            {"username": "test_user", "password": "test_password"}
            """

        When we get "/users"
        Then we get list with 2 items
            """
            {"_items": [{"username": "foo", "_etag": "#USERS._etag#"}, {"username": "test_user"}]}
            """

    Scenario: user logs in locks content and logs out logs in again and the content is no longer locked
        Given "users"
            """
            [{"username": "foo", "password": "bar", "email": "foo@bar.org", "is_active": true, "user_type": "administrator"}]
            """
        When we post to auth
        """
        {"username": "foo", "password": "bar"}
        """
        Given "archive"
        """
        [{"_id": "item-1", "guid": "item-1", "headline": "test", "_current_version": 1}]
        """
        When we post to "/archive/item-1/lock"
        """
        {}
        """
        When we delete "/auth/#AUTH_ID#"
        """
        {}
        """
        Then we get response code 204
        When we post to auth
        """
        {"username": "foo", "password": "bar"}
        """
        When we get "/archive"
        Then item "item-1" is unlocked
