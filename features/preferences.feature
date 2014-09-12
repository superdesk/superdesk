
Feature: User preferences

    @auth
    Scenario: List empty preferences
        Given empty "preferences"
        When we get "/preferences"
        Then we get list with 0 items
        
	@auth
    Scenario: Create new preference
        Given empty "users"
        When we post to "/users"
        """
        {"username": "foo", "password": "barbar", "email": "foo@bar.com"}
        """
        And we get "/users/foo"
        Then we get existing resource
        """
        {"username": "foo"}
        """
        When we get "/preferences"
        Then we get list with 1 items
        """
        {"_items": [{"_id": "#USERS_ID#", "_links": {"self": {"title": "Preference", "href": "/preferences/#USERS_ID#"}}}]}
        """


	@auth
	Scenario: Update preference settings
		Given empty "users"
		When we post to "/users"
        """
        {"username": "foo", "password": "bar", "email": "foo@bar.com"}
        """
	    Given "preferences"
	    """
	    [{"_id": "#USERS_ID#"}]
	    """
	    When we patch "/preferences/#USERS_ID#"
	    """
	    {"settings": {"send me email when I'm mentioned": "yes"}
	    """
	    And we get "users/foo"
	    Then we get updated response
	    """
	    {"username": "foo", "settings": {send me email when I'm mentioned: "yes"}
	    """
	    
	@auth
    Scenario: (Fail) - wrong url
		Given empty "users"
		When we post to "/users"
        """
        {"username": "foo", "password": "bar", "email": "foo@bar.com"}
        """
	    Given "preferences"
	    """
	    [{"_id": "#USERS_ID#"}]
	    """
	    When we patch "/preferences/#USERS_ID#"
	    """
	    {"settings": {"send me email when I'm mentioned": "yes"}
	    """
        Then we get error 404
        """
        {"_error": {"code": 404, "message": "The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again."}, "_status": "ERR"}
      	"""
