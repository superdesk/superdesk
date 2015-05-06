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
        {"username": "foo", "email": "foo@bar.com", "is_active": true, "sign_off": "abc"}
        """
        When we post to "/groups"
        """
        {"name": "Sports group", "members": [{"user": "#user._id#"}]}
        """
        And we get "/groups"
        Then we get list with 1 items
        """
        {"_items": [{"name": "Sports group", "members": [{"user": "#user._id#"}]}]}
        """
        When we get "/users/#user._id#/groups"
        Then we get list with 1 items
        """
        {"_items": [{"name": "Sports group", "members": [{"user": "#user._id#"}]}]}
        """


    @auth
    Scenario: Update group
        Given empty "groups"
        When we post to "users"
        """
        {"username": "foo", "email": "foo@bar.com", "is_active": true, "sign_off": "abc"}
        """
        When we post to "/groups"
        """
        {"name": "Sports group"}
        """
        And we patch latest
        """
        {"name": "Sports group", "members": [{"user": "#user._id#"}]}
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


    @auth @test
    Scenario: Unique name for group
      Given empty "groups"
      When we post to "/groups"
      """
      {"name": "Sports group"}
      """
      Then we get OK response
      When we post to "/groups"
      """
      {"name": "sports GrouP"}
      """
      Then we get response code 400
      When we post to "/groups"
      """
      {"name": "Sports Group users"}
      """
      Then we get OK response
      When we patch "/groups/#groups._id#"
      """
      {"name": "sPorts GrouP"}
      """
      Then we get response code 400