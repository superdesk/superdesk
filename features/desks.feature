Feature: Desks

    @auth
    Scenario: Empty desks list
        Given empty "desks"
        When we get "/desks"
        Then we get list with 0 items

    @auth
    Scenario: Create new desk
        Given empty "users"
        Given empty "desks"
        When we post to "users"
            """
            {"username": "foo", "email": "foo@bar.com", "is_active": true}
            """
        When we post to "/desks"
            """
            {"name": "Sports Desk", "members": [{"user": "#USERS_ID#"}]}
            """
        And we get "/desks"
        Then we get list with 1 items
            """
            {"_items": [{"name": "Sports Desk", "members": [{"user": "#USERS_ID#"}]}]}
            """
        When we get the default incoming stage
        And we delete latest
        Then we get error 403
        """
        {"_status": "ERR", "_message": "Deleting default stages is not allowed."}
        """

	@auth
	Scenario: Update desk
	    Given empty "desks"
		When we post to "/desks"
            """
            {"name": "Sports Desk"}
            """
		And we patch latest
			 """
            {"name": "Sports Desk modified"}
             """
		Then we get updated response

	@auth
	Scenario: Delete desk
		Given "desks"
			"""
			[{"name": "test_desk1"}]
			"""
		When we post to "/desks"
        	"""
            [{"name": "test_desk2"}]
            """
        And we delete latest
        Then we get deleted response
