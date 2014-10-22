Feature: Groups

    @auth
    Scenario: Empty groups list
        Given empty "groups"
        When we get "/groups"
        Then we get list with 0 items

    @auth
    Scenario: Create new group
        Given empty "users"
        Given empty "groups"
        When we post to "users"
        """
        {"username": "foo", "email": "foo@bar.com", "is_active": true}
        """
        When we post to "/groups"
        """
        {"name": "Sports group", "members": [{"user": "#USERS_ID#"}]}
        """
        And we get "/groups"
        Then we get list with 1 items
        """
        {"_items": [{"name": "Sports group", "members": [{"user": "#USERS_ID#"}]}]}
        """
        When we get "/users/#USERS_ID#/groups"
        Then we get list with 1 items
        """
        {"_items": [{"name": "Sports group", "members": [{"user": "#USERS_ID#"}]}]}
        """


    @auth
    Scenario: Update group
        Given empty "groups"
        When we post to "users"
        """
        {"username": "foo", "email": "foo@bar.com", "is_active": true}
        """
        When we post to "/groups"
        """
        {"name": "Sports group"}
        """
        And we patch latest
        """
        {"name": "Sports group", "members": [{"user": "#USERS_ID#"}]}
        """
        Then we get updated response

    @auth
    Scenario: Delete group
        Given "groups"
        """
        [{"name": "test_group1"}]
        """
        When we post to "/groups"
        """
        [{"name": "test_group2"}]
        """
        And we delete latest
        Then we get deleted response
