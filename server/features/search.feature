Feature: Search Feature

    @auth
    Scenario: Can search ingest
        Given "ingest"
            """
            [{"guid": "1"}]
            """
        When we get "/search"
        Then we get list with 1 items

    @auth
    Scenario: Can search archive
        Given "desks"
        """
        [{"name": "Sports Desk", "spike_expiry": 60}]
        """
        Given "archive"
            """
            [{"guid": "1", "task": {"desk": "#desks._id#"}}]
            """
        When we get "/search"
        Then we get list with 1 items

    @auth
    Scenario: Can not search private content
        Given "archive"
            """
            [{"guid": "1"}]
            """
        When we get "/search"
        Then we get list with 0 items

    @auth
    Scenario: Can limit search to 1 result per shard
        Given "desks"
        """
        [{"name": "Sports Desk", "spike_expiry": 60}]
        """
        Given "archive"
        """
        [{"guid": "1", "task": {"desk": "#desks._id#"}}, {"guid": "2", "task": {"desk": "#desks._id#"}},
         {"guid": "3", "task": {"desk": "#desks._id#"}}, {"guid": "4", "task": {"desk": "#desks._id#"}},
         {"guid": "5", "task": {"desk": "#desks._id#"}}, {"guid": "6", "task": {"desk": "#desks._id#"}},
         {"guid": "7", "task": {"desk": "#desks._id#"}}, {"guid": "8", "task": {"desk": "#desks._id#"}},
         {"guid": "9", "task": {"desk": "#desks._id#"}}]
        """
        Then we set elastic limit
        When we get "/search"
        Then we get list with 5 items

    @auth
    Scenario: Search Invisible stages without desk membership
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
            {"_items": [{"name": "Sports Desk", "members": [{"user": "#users._id#"}]}]}
            """
        When we get the default incoming stage
        When we post to "/archive"
            """
            [{"guid": "item1", "task": {"desk": "#desks._id#",
            "stage": "#desks.incoming_stage#", "user": "#users._id#"}}]
            """
        Then we get response code 201
        When we get "/search"
        Then we get list with 1 items
        When we patch "/stages/#desks.incoming_stage#"
            """
            {"is_visible": false}
            """
        Then we get response code 200
        When we get "/search"
        Then we get list with 0 items
        When we get "/archive/#archive._id#"
        Then we get response code 403


    @auth
    Scenario: Search Invisible stages with desk membership
        Given empty "desks"
        When we post to "users"
            """
            {"username": "foo", "email": "foo@bar.com", "is_active": true, "sign_off": "abc"}
            """
        When we post to "/desks"
            """
            {"name": "Sports Desk", "members": [{"user": "#users._id#"}, {"user": "#CONTEXT_USER_ID#"}]}
            """
        And we get "/desks"
        Then we get list with 1 items
            """
            {"_items": [{"name": "Sports Desk", "members": [{"user": "#users._id#"}, {"user": "#CONTEXT_USER_ID#"}]}]}
            """
        When we get the default incoming stage
        When we post to "/archive"
            """
            [{"guid": "item1", "task": {"desk": "#desks._id#",
            "stage": "#desks.incoming_stage#", "user": "#users._id#"}}]
            """
        Then we get response code 201
        When we get "/search"
        Then we get list with 1 items
        When we patch "/stages/#desks.incoming_stage#"
            """
            {"is_visible": false}
            """
        Then we get response code 200
        When we get "/search"
        Then we get list with 1 items
        When we get "/archive/#archive._id#"
        Then we get response code 200