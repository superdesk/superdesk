Feature: Desks

    @auth
    Scenario: Empty desks list
        Given empty "desks"
        When we get "/desks"
        Then we get list with 0 items

    @auth
    @notification
    Scenario: Create new desk
        Given empty "users"
        Given empty "desks"
        When we post to "users"
            """
            {"username": "foo", "email": "foo@bar.com", "is_active": true, "sign_off": "abc"}
            """
        When we post to "/desks"
            """
            {"name": "Sports Desk", "members": [{"user": "#users._id#"}]}
            """
        And we get "/desks"
        Then we get list with 1 items
            """
            {"_items": [{"name": "Sports Desk", "members": [{"user": "#users._id#"}], "desk_type": "authoring"}]}
            """
        Then we get notifications
            """
            [{"event": "desk", "extra": {"created": 1, "desk_id": "#desks._id#"}}]
            """
        When we get the default incoming stage
        And we delete latest
        Then we get error 412
        """
        {"_status": "ERR", "_message": "Cannot delete a default stage."}
        """

	@auth
    @notification
	Scenario: Update desk
	    Given empty "desks"
		When we post to "/desks"
            """
            {"name": "Sports Desk", "desk_type": "production"}
            """
		And we patch latest
			 """
            {"name": "Sports Desk modified"}
             """
		Then we get updated response
            """
            {"name": "Sports Desk modified", "desk_type": "production"}
            """
        Then we get notifications
            """
            [{"event": "desk", "extra": {"updated": 1, "desk_id": "#desks._id#"}}]
            """

	@auth
    @notification
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
        Then we get notifications
        """
        [{"event": "desk", "extra": {"deleted": 1, "desk_id": "#desks._id#"}}]
        """
        Then we get deleted response

	@auth
	Scenario: Desk name must be unique.
	    Given empty "desks"
		When we post to "/desks"
            """
            {"name": "Sports Desk"}
            """
        Then we get OK response
		When we post to "/desks"
			 """
            {"name": "sports desk"}
             """
		Then we get response code 400
		When we post to "/desks"
			 """
            {"name": "Sports Desk 2"}
             """
        Then we get OK response
		When we patch "/desks/#desks._id#"
			 """
            {"name": "SportS DesK"}
             """
		Then we get response code 400

    @auth
    Scenario: Cannot delete desk if it is assigned as a default desk to user(s)
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
        And we delete "/desks/#desks._id#"
        Then we get error 412
        """
        {"_message": "Cannot delete desk as it is assigned as default desk to user(s)."}
        """

    @auth
    @notification
    Scenario: Remove user from desk membership
        Given "users"
        """
        [{"username": "foo", "email": "foo@bar.com", "is_active": true}]
        """
        And "desks"
        """
        [{"name": "Sports Desk", "members": [{"user": "#users._id#"}]}]
        """
        When we patch "/desks/#desks._id#"
        """
        { "members": []}
        """
        Then we get updated response
        Then we get notifications
        """
        [{"event": "desk_membership_revoked", "extra": {"updated": 1, "user_ids": ["#users._id#"]}}]
        """

    @auth
    Scenario: Set the monitoring settings
        Given "users"
        """
        [{"username": "foo", "email": "foo@bar.com", "is_active": true}]
        """
        And "desks"
        """
        [{"name": "Sports Desk", "members": [{"user": "#users._id#"}]}]
        """
        When we patch "/desks/#desks._id#"
        """
        { "monitoring_settings": [{"_id": "id_stage", "type": "stage", "max_items": 10}, 
                                  {"_id": "id_saved_search", "type": "search", "max_items": 20},
                                  {"_id": "id_personal", "type": "personal", "max_items": 15}
                                 ]
        }
        """
        Then we get updated response
        When we get "/desks"
        Then we get list with 1 items
            """
            {"_items": [{"name": "Sports Desk", 
                          "monitoring_settings": [{"_id": "id_stage", "type": "stage", "max_items": 10}, 
                                                  {"_id": "id_saved_search", "type": "search", "max_items": 20},
                                                  {"_id": "id_personal", "type": "personal", "max_items": 15}
                                                 ]
                        }]
            }
            """

	@auth
    @notification @test
	Scenario: Update desk type
        Given we have "desks" with "SPORTS_DESK_ID" and success
        """
        [{"name": "Sports", "desk_type": "authoring"}]
        """
        When we post to "archive"
        """
        [{  "type":"text", "headline": "test1", "guid": "123", "state": "submitted",
            "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
        """
        And we get "/archive/123"
        Then we get existing resource
        """
        {"headline": "test1", "sign_off": "abc"}
        """
		When we patch "/desks/#desks._id#"
        """
         {"name": "Sports Desk modified", "desk_type": "production"}
        """
        Then we get OK response
		When we patch "/desks/#desks._id#"
        """
         {"name": "Sports Desk modified", "desk_type": "authoring"}
        """
        Then we get OK response
        When we post to "/desks" with "FINANCE_DESK_ID" and success
        """
        [{"name": "Finance", "desk_type": "production" }]
        """
        And we switch user
        And we post to "/archive/123/move"
        """
        [{"task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]
        """
        Then we get OK response
        When we get "/archive/123"
        Then we get existing resource
        """
        { "operation": "move", "headline": "test1", "guid": "123", "state": "submitted", "_current_version": 2, "sign_off": "abc/foo",
          "task": {
            "desk": "#desks._id#",
            "stage": "#desks.incoming_stage#",
            "last_authoring_desk": "#SPORTS_DESK_ID#"
            }
        }
        """
        And there is no "last_production_desk" in task
		When we patch "/desks/#SPORTS_DESK_ID#"
        """
        {"name": "Sports Desk modified", "desk_type": "production"}
        """
        Then we get error 400
        """
        {"_issues": {"validator exception": "400: Cannot update Desk Type as there are article(s) referenced by the Desk."}}
        """