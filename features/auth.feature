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
        Then we get error 400
        """
        {"_message": "", "_issues": "The provided old password is not correct.", "_status": "ERR"}
        """        
        
        
	Scenario: Reset password existing user
        Given "users"
        """
        [{"username": "foo", "password": "bar", "email": "foo@bar.org", "is_active": true}]
        """

        When we post to reset_password we get email with token
        And we reset password for user

    Scenario: Reset password disabled user
        Given "users"
        """
        [{"username": "foo", "password": "bar", "email": "foo@bar.org", "is_active": false}]
        """

        When we post to reset_password we do not get email with token

    @auth
    Scenario: Reset password existing user - disabled after mail is sent
        Given "users"
        """
        [{"username": "foo", "password": "bar", "email": "foo@bar.org", "is_active": true}]
        """

        When we post to reset_password we get email with token
        When we change user status to "inactive" using "/users/foo"
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

        Then we get error 400
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
