Feature: Content Locking

    @auth
    Scenario: Lock item and edit
        Given "archive"
        """
        [{"_id": "item-1", "guid": "item-1", "headline": "test"}]
        """
        When we post to "/archive/item-1/lock"
        """
        {}
        """
        Then we get new resource
        """
        {"_id": "item-1", "guid": "item-1", "headline": "test"}
        """
        And item "item-1" is assigned
        When we patch "/archive/item-1"
        """
        {"headline": "test 2"}
        """
        Then we get OK response

    @auth
    Scenario: Unlocking version 0 draft item deletes the item
        Given "archive"
        """
        [{"_id": "item-1", "guid": "item-1", "headline": "test", "_current_version": 0, "state": "draft"}]
        """
        When we post to "/archive/item-1/lock"
        """
        {}
        """
        Then we get new resource
        """
        {"_id": "item-1", "guid": "item-1", "headline": "test"}
        """

        When we post to "/archive/item-1/unlock"
        """
        {}
        """
        And we get "/archive/item-1"
        Then we get error 404

    @auth
    Scenario: Unlocking version 1+ item unlockes the item
        Given "archive"
        """
        [{"_id": "item-1", "guid": "item-1", "headline": "test", "_current_version": 1}]
        """
        When we post to "/archive/item-1/lock"
        """
        {}
        """
        Then we get new resource
        """
        {"_id": "item-1", "guid": "item-1", "headline": "test"}
        """

        When we post to "/archive/item-1/unlock"
        """
        {}
        """
        And we get "/archive/item-1"
        Then we get response code 200

    @auth
    Scenario: Fail edit on locked item
        Given "archive"
        """
        [{"_id": "item-1", "guid": "item-1", "headline": "test"}]
        """
        When we post to "/archive/item-1/lock"
        """
        {}
        """
        And we switch user
        And we patch "/archive/item-1"
        """
        {"headline": "test 2"}
        """
        Then we get error 400

    @auth
    Scenario: Fail to force unlock for other User workspace content
        Given "archive"
        """
        [{"_id": "item-1", "guid": "item-1", "headline": "test"}]
        """
        When we post to "/archive/item-1/lock"
        """
        {}
        """
        Then we get new resource
        """
        {"_id": "item-1", "guid": "item-1", "headline": "test"}
        """
        And item "item-1" is locked
        When we switch user
        And we post to "/archive/item-1/unlock"
        """
        {}
        """
        Then we get error 403


    @auth
    Scenario: Force unlock other user content on a desk with desk membership.
        Given "desks"
        """
        [{"name": "Sports", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
        """
        Given "archive"
        """
        [{"_id": "item-1", "guid": "item-1", "headline": "test", "_current_version": 2,
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
        """
        When we post to "/archive/item-1/lock"
        """
        {}
        """
        Then we get new resource
        """
        {"_id": "item-1", "guid": "item-1", "headline": "test"}
        """
        And item "item-1" is locked
        When we switch user
        When we patch "/desks/#desks._id#"
        """
        {"members":[{"user":"#USERS_ID#"},{"user":"#CONTEXT_USER_ID#"}]}
        """
        And we post to "/archive/item-1/unlock"
        """
        {}
        """
        Then we get new resource
        """
        {"_id": "item-1", "guid": "item-1", "headline": "test"}
        """
        And item "item-1" is unlocked


    @auth
    Scenario: Fail force unlock other user content on a desk with out desk membership.
        Given "desks"
        """
        [{"name": "Sports", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
        """
        Given "archive"
        """
        [{"_id": "item-1", "guid": "item-1", "headline": "test",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
        """
        When we post to "/archive/item-1/lock"
        """
        {}
        """
        Then we get new resource
        """
        {"_id": "item-1", "guid": "item-1", "headline": "test"}
        """
        And item "item-1" is locked
        When we switch user
        And we post to "/archive/item-1/unlock"
        """
        {}
        """
        Then we get error 403


    @auth @test
    Scenario: Fail lock if item is locked in another session
        Given "archive"
        """
        [{"_id": "item-1", "guid": "item-1", "headline": "test"}]
        """
        When we post to "/archive/item-1/lock"
        """
        {}
        """
        Then we get new resource
        """
        {"_id": "item-1", "guid": "item-1", "headline": "test"}
        """
        And item "item-1" is locked
        When we setup test user
        When we post to "/archive/item-1/lock"
        """
        {}
        """
        Then we get error 403


    @auth
    Scenario: Force unlock if item is locked in another session
        Given "archive"
        """
        [{"_id": "item-1", "guid": "item-1", "headline": "test", "_current_version": 2}]
        """
        When we post to "/archive/item-1/lock"
        """
        {}
        """
        Then we get new resource
        """
        {"_id": "item-1", "guid": "item-1", "headline": "test"}
        """
        And item "item-1" is locked
        When we setup test user
        When we post to "/archive/item-1/unlock"
        """
        {}
        """
        Then we get new resource
        """
        {"_id": "item-1", "guid": "item-1", "headline": "test"}
        """
        And item "item-1" is unlocked


    @auth
    Scenario: Fail force unlock if you don't have privileges to unlock
        Given "desks"
        """
        [{"name": "Sports", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
        """
        Given "archive"
        """
        [{"_id": "item-1", "guid": "item-1", "headline": "test",
        "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
        """
        When we post to "/archive/item-1/lock"
        """
        {}
        """
        Then we get new resource
        """
        {"_id": "item-1", "guid": "item-1", "headline": "test"}
        """
        And item "item-1" is locked
        When we switch user
        When we patch "/desks/#desks._id#"
        """
        {"members":[{"user":"#USERS_ID#"},{"user":"#CONTEXT_USER_ID#"}]}
        """
        Then we get OK response
        When we patch "/users/#USERS_ID#"
        """
        {"user_type": "user", "privileges": {"archive":1}}
        """
        Then we get OK response
        When we post to "/archive/item-1/unlock"
        """
        {}
        """
        Then we get error 403

