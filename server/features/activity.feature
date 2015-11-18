Feature: User Activity

    @auth
    Scenario: User activity
         When we post to "/users"
            """
            {"username": "foo", "password": "barbar", "email": "foo@bar.com", "is_active": true, "sign_off": "abc"}
            """

         Then we get response code 201
         When we get "/activity/"
         Then we get existing resource
         	"""
         	{"_items": [{"data": {"user": "foo"}, "message": "created user {{user}}"}]}
         	"""

         When we delete "/users/foo"
         Then we get response code 204

         When we get "/activity/"
         Then we get existing resource
         	"""
         	{"_items": [{"data": {"user": "foo"}, "message": "disabled user {{user}}"}]}
         	"""

    @auth
    Scenario: Image archive activity
        Given empty "archive"
        When we upload a file "bike.jpg" to "archive"

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
        [{"name": "first stage", "desk": "#desks._id#"}]
		"""
        Given "archive"
        """
        [{"guid": "tag:example.com,0000:newsml_BRE9A605"}]
        """

        When we patch "/tasks/tag:example.com,0000:newsml_BRE9A605"
        """
        {"task":{"user":"#user._id#","stage":"#stages._id#","desk":"#desks._id#"}}
        """
        Then we get existing resource
        """
        {"task":{"user":"#user._id#","stage":"#stages._id#","desk":"#desks._id#"}}
        """

        When we get "/activity?where={"desk": "#desks._id#"}"
        Then we get existing resource
        """
        {"_items": [{"user":"#user._id#", "item":"tag:example.com,0000:newsml_BRE9A605", "desk":"#desks._id#"}]}
        """

        When we get "/activity?where={"desk": "invalid_desk_id"}"
        Then we get list with 0 items

    @auth
    Scenario: Read notification by a user who is not meant to:
        Given empty "comments"
        When we post to "/users"
        """
        {"username": "joe", "display_name": "Joe Black", "email": "joe@black.com", "is_active": true, "sign_off": "abc"}
        """
        When we mention user in comment for "/comments"
        """
        [{"text": "test comment @no_user with one user mention @joe", "item": "xyz"}]
        """
        Then we get activity
        When we patch "/activity/#activity._id#"
        """
        {"read":{"#users._id#":1}}
        """
        Then we get error 400

    @auth
    Scenario: Read notification successful :
        Given empty "comments"
        When we mention user in comment for "/comments"
        """
        [{"text": "test comment @no_user with one user mention @test_user", "item": "xyz"}]
        """
        Then we get activity
        When we patch "/activity/#activity._id#"
        """
        {"read":{"#user._id#":1}}
        """
        Then we get error 200

    @auth
    Scenario: Read notification attempt bad transition :
        Given empty "comments"
        When we mention user in comment for "/comments"
        """
        [{"text": "test comment @no_user with one user mention @test_user", "item": "xyz"}]
        """
        Then we get activity
        When we patch "/activity/#activity._id#"
        """
        {"read":{"#users._id#":0}}
        """
        Then we get error 400

 	@auth
	Scenario: Verify if activity was created on archive operations
		Given empty "activity"
		Given empty "archive"
        When we post to "/archive" with success
        """
        [{"guid": "some-global-unique-id", "type": "text"}]
        """
        And we patch "/archive/some-global-unique-id"
        """
        {"headline": "test"}
        """
        And we get "/activity"
        Then we get list with 2 items
        """
        {"_items": [
        		{"item": "some-global-unique-id",
        		 "message": "added new {{ type }} item with empty header/title",
        		 "data": {"type": "text", "subject": "__any_value__"}},
        		{"item": "some-global-unique-id",
        		 "message": "created new version {{ version }} for item {{ type }} about \"{{ subject }}\"",
        		 "data": {"version": 2, "type": "text", "subject": "test"}}]}
        """
