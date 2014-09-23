@wip
Feature: User preferences

    @auth
    Scenario: List empty preferences
        Given empty "preferences"
        When we get "/preferences"
        Then we get error 405
        """
        {"_error": {"message": "The method is not allowed for the requested URL.", "code": 405}, "_status": "ERR"}
        """


    @auth
    Scenario: Create new preference
        Given "users"
        """
        [{"username": "foo", "password": "barbar", "email": "foo@bar.com"}]
        """

        When we get "/preferences/#USERS_ID#"
        Then we get default preferences


    @auth
    Scenario: Update preference settings
        Given "users"
        """
        [{"username": "foo", "password": "bar", "email": "foo@bar.com"}]
        """

        When we patch "/preferences/#USERS_ID#"
        """
        {"preferences": {"email:notification": {"enabled": "false"}}}
        """
        Then we get updated response

        When we get "/preferences/#USERS_ID#"
        Then we get existing resource
        """
        {"_id": "#USERS_ID#", "preferences": {"email:notification": {"enabled": "false"}}}
        """

    @auth
    Scenario: Update preference settings - wrong preference
        Given "users"
        """
        [{"username": "foo", "password": "bar", "email": "foo@bar.com"}]
        """

        When we patch "/preferences/#USERS_ID#"
        """
        {"preferences": {"email:bad_name": {"enabled": "false"}}}
        """
        Then we get error 400
        """
        {"_status": "ERR", "_issues": {"validator exception": "Invalid preference: email:bad_name"}}
	    """
