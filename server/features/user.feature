Feature: User Resource

    @auth
    @dbauth
    Scenario: Create a user
        Given empty "users"
        When we create a new user
        """
        {"username": "foo", "password": "barbar", "email": "foo@bar.com"}
        """
        Then we get new resource
        """
        {"username": "foo", "display_name": "foo", "email": "foo@bar.com", "is_active": false, "needs_activation": true}
        """
        And we get no "password"
        And we get activation email

    @auth
    Scenario: Create user with valid email
        Given empty "users"
        When we post to "/users"
        """
        {"username": "foo", "password": "barbar", "email": "foo@bar.com.au"}
        """
        Then we get response code 201

    @auth
    Scenario: Test email validation
        Given empty "users"
        When we post to "/users"
        """
        {"username": "foo", "password": "barbar", "email": "invalid email"}
        """
        Then we get error 400
        """
        {"_status": "ERR", "_issues": {"email": {"pattern": 1}}}
        """

    @auth
    Scenario: Test unique validation
        Given "users"
        """
        [{"username": "foo", "email": "foo@bar.com", "is_active": true}]
        """
        When we post to "/users"
        """
        {"username": "foo", "email": "foo@bar.com", "is_active": true}
        """
        Then we get error 400
        """
        {"_status": "ERR", "_issues": {"email": {"unique": 1}, "username": {"unique": 1}}}
        """

    @auth
    @dbauth
    Scenario: Test phone validation
        Given empty "users"
        When we post to "/users"
        """
        {"username": "foo", "password": "barbar", "email": "foo@bar.com", "phone": "0123", "is_active": true}
        """
        Then we get error 400
        """
        {"_issues": {"phone": {"pattern": 1}}, "_status": "ERR"}
        """

    @auth
    Scenario: List users
        Given "users"
        """
        [{"username": "foo", "email": "foo@bar.org", "is_active": true}, {"username": "bar", "email": "foo@bar.or", "is_active": true}]
        """
        When we get "/users"
        Then we get list with +2 items

    @auth
    Scenario: Fetch single user
        Given "users"
        """
        [{"username": "foo", "first_name": "Foo", "last_name": "Bar", "email": "foo@bar.org", "is_active": true}]
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
        [{"username": "foo", "email": "foo@bar.org", "is_active": true}]
        """
        When we switch user
        And we delete "/users/foo"
        Then we get response code 204

    @auth
    @dbauth
    Scenario: Update user
        Given "users"
        """
        [{"username": "foo", "email": "foo@bar.org", "is_active": true}]
        """
        When we patch "/users/foo"
        """
        {"first_name": "Testing"}
        """
        Then the field "display_name" value is "Testing"

    @auth
    @dbauth
    Scenario: Update user first name
        Given "users"
        """
        [{"username": "foo", "email": "foo@bar.org", "first_name": "first", "last_name": "last", "is_active": true}]
        """
        When we patch "/users/foo"
        """
        {"first_name": "Testing"}
        """
        Then the field "display_name" value is "Testing last"

    @auth
    @dbauth
    Scenario: Update user last name
        Given "users"
        """
        [{"username": "foo", "email": "foo@bar.org", "first_name": "first", "last_name": "last", "is_active": true}]
        """
        When we patch "/users/foo"
        """
        {"last_name": "Testing"}
        """
        Then the field "display_name" value is "first Testing"

    @auth
    Scenario: Change user status
        Given "users"
        """
        [{"username": "foo", "email": "foo@bar.co", "is_active": true}]
        """
        When we change user status to "enabled but inactive" using "/users/foo"
        """
        {"is_active": false}
        """
        Then we get updated response
        When we change user status to "enabled and active" using "/users/foo"
        """
        {"is_active": true}
        """
        Then we get updated response

    @auth
    Scenario: User workspace
        Given "users"
        """
        [{"username": "foo", "workspace": {"name": "my workspace"}, "email": "foo@bar.org", "is_active": true}]
        """
        When we get "/users/foo"
        Then we get existing resource
        """
        {"username": "foo", "workspace": {}}
        """

    @auth
    Scenario: Create a user with default role
        Given "roles"
        """
        [{"name": "A", "is_default": true, "_id":1}]
        """
        When we post to "/users"
        """
        {"username": "foo", "password": "barbar", "email": "foo@bar.com"}
        """
        Then we get new resource
        """
        {"username": "foo", "display_name": "foo", "role": 1}
        """

    @auth
    Scenario: Create a user with no default role
        Given "roles"
        """
        [{"name": "A", "is_default": false, "_id": 1}]
        """
        When we post to "/users"
        """
        {"username": "foo", "password": "barbar", "email": "foo@bar.com"}
        """
        Then we get new resource
        """
        {"username": "foo", "display_name": "foo", "role": null}
        """

    @auth
    Scenario: A logged-in user can't delete themselves from the system
        Given we login as user "foo" with password "bar"
        When we delete "/users/#user._id#"
        Then we get error 403

    @auth
    Scenario: A logged-in user can't change role
        Given "roles"
        """
        [{"name": "A", "is_default": true}, {"name": "B"}]
        """
        And we login as user "foo" with password "bar"
        """
        {"user_type": "user", "email": "foo.bar@foobar.org"}
        """
        When we get "/users/foo"
        Then we get existing resource
        """
        {"username": "foo", "display_name": "foo", "user_type": "user"}
        """
        When we patch "/users/#CONTEXT_USER_ID#"
        """
        {"role": "#roles._id#"}
        """
        Then we get error 400
        """
        {"_status": "ERR", "_issues": {"validator exception": "403: Insufficient privileges to update role/user_type/privileges"}}
        """

    @auth
    Scenario: User gets invisible stages
        Given empty "users"
        Given empty "desks"
        Given empty "stages"
        When we post to "users"
        """
        {"username": "foo", "email": "foo@bar.com", "is_active": true}
        """
        Given "desks"
        """
        [{"name": "Sports Desk", "members": [{"user": "#users._id#"}]}]
        """
        When we post to "desks"
        """
        [{"name": "News Desk"}]
        """
        And we post to "/stages"
        """
        {
        "name": "invisible1",
        "task_status": "todo",
        "desk": "#desks._id#",
        "is_visible" : false
        }
        """

        When we post to "/stages"
        """
        {
        "name": "invisible2",
        "task_status": "todo",
        "desk": "#desks._id#",
        "is_visible" : false
        }
        """

        Then we get 2 invisible stages for user
        """
        {"user": "#users._id#"}
        """

    @auth
    Scenario: Assign a default desk to user
        Given "users"
        """
        [{"username": "foo", "email": "foo@bar.com", "is_active": true}]
        """
        And "desks"
        """
        [{"name": "Sports Desk", "members": [{"user": "#users._id#"}]}]
        """
        When we patch "/users/#users._id#"
        """
        {"desk": "#desks._id#"}
        """
        Then we get existing resource
        """
        {"username": "foo", "desk": "#desks._id#"}
        """
