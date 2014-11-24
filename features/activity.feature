Feature: User Activity

    @auth
    Scenario: User activity
         When we post to "/users"
            """
            {"username": "foo", "password": "barbar", "email": "foo@bar.com", "is_active": true}
            """
            
         Then we get response code 201
         When we get "/activity/"
         Then we get existing resource
         	"""
         	{"_items": [{"data": {"user": "foo"}, "message": "created user {{user}}"}]}
         	"""
         	
         When we delete "/users/foo"
         Then we get response code 200
         
         When we get "/activity/"
         Then we get existing resource
         	"""
         	{"_items": [{"data": {"user": "foo"}, "message": "removed user {{user}}"}]}
         	"""

    @auth
    Scenario: Image archive activity
        Given empty "archive"
        When we upload a file "bike.jpg" to "archive_media"
     	
     	When we get "/activity/"
        Then we get existing resource
         	"""
         	{"_items": [{"data": {"renditions": {}, "name": "image/jpeg"}, "message": "uploaded media {{ name }}"}]}
         	"""

	@auth
	Scenario: Filter activity by desk
		Given empty "activity"
		Given "desks"
		"""
		[{"name": "test_desk1"}]
		"""
		Given "stages"
		"""
        [{"name": "first stage", "desk": "#DESKS_ID#"}]
		"""
        Given "archive"
        """
        [{"guid": "tag:example.com,0000:newsml_BRE9A605"}]
        """

        When we patch "/tasks/tag:example.com,0000:newsml_BRE9A605"
        """
        {"task":{"user":"#USER_ID#","stage":"#STAGES_ID#","desk":"#DESKS_ID#"}}
        """
        Then we get existing resource
        """
        {"task":{"user":"#USER_ID#","stage":"#STAGES_ID#","desk":"#DESKS_ID#"}}
        """

        When we get "/activity?where={"desk": "#DESKS_ID#"}"
        Then we get existing resource
        """
        {"_items": [{"user":"#USER_ID#", "item":"tag:example.com,0000:newsml_BRE9A605", "desk":"#DESKS_ID#"}]}
        """

        When we get "/activity?where={"desk": "invalid_desk_id"}"
        Then we get list with 0 items
