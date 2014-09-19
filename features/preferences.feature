@wip
Feature: User preferences

    @auth
    Scenario: List empty preferences
        Given empty "preferences"
        When we get "/preferences"
        Then we get list with 0 items

    @auth
    Scenario: List available preferences
        When we get "/available_preferences"
        Then we get list with 1 items
        
	@auth
    Scenario: Create new preference
        Given "users"
            """
            [{"username": "foo", "password": "barbar", "email": "foo@bar.com"}]
            """

        When we get "/preferences"
        Then we get list with 1 items


	@auth
	Scenario: Update preference settings
		Given "users"
            """
            [{"username": "foo", "password": "bar", "email": "foo@bar.com"}]
            """

        When we patch "/preferences/#USERS_ID#"
	       """
	       {"preferences": {"email_notification": {"options": "off"}}}
	       """
	    Then we get updated response

        When we get "/preferences/#USERS_ID#"
        Then we get existing resource
            """
            {"_id": "#USERS_ID#", "preferences": {"email_notification": {"options": "off"}}}
            """
