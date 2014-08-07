Feature: Planning Item Coverages

    @auth
    Scenario: List empty coverages
        Given empty "coverages"
        When we get "/coverages"
        Then we get list with 0 items
        
    @auth
    Scenario: Create new coverage
    	Given empty "users"
        Given empty "coverages"
        When we post to "users"
	        """
	        {"username": "foo", "email": "foo@bar.com"}
	        """
        When we post to "coverages"
	        """
	        [{"headline": "first coverage", "assigned_user": "#USERS_ID#"}]
	        """
        And we get "/coverages"
        Then we get list with 1 items
	        """
	        {"headline": "first coverage", "assigned_user": "#USERS_ID#"}
	        """

    @auth
    Scenario: Update coverage
	   	Given "coverages"
	        """
	        [{"headline": "testCoverage"}]
	        """
	        
	    When we patch given
	        """
	        {"ed_note":"the test coverage modified"}
	        """
	
	    And we patch latest
	        """
	        {"ed_note":"the test of the test coverage modified"}
	        """
	
	   	Then we get updated response
   	
   	@auth
	Scenario: Update coverage
		Given empty "desks"
	    Given empty "coverages"
	    When we post to "desks"
		    """
            {"name": "Sports Desk"}
            """
		When we post to "coverages"
            """
            [{"headline": "second coverage"}]
            """
		And we patch latest
			 """
            {"ed_note": "second coverage modified", "assigned_desk":"#DESKS_ID#"}
             """
		Then we get updated response
		
	@auth
	Scenario: Delete coverage
		Given empty "coverages"
		When we post to "coverages"
			"""
			[{"headline": "test_coverage1"}]
			"""
        And we delete latest
        Then we get deleted response


		