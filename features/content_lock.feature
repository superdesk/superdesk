@wip
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
        Then we get OK response

        When we patch "/archive/item-1"
            """
            {"headline": "test 2"}
            """

        Then we get OK response

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
    Scenario: Force unlock
        Given "archive"
            """
            [{"_id": "item-1", "guid": "item-1", "headline": "test"}]
            """

        When we post to "/archive/item-1/lock"
            """
            {}
            """
        Then item "item-1" is locked

        When we switch user
        And we post to "/archive/item-1/unlock"
            """
            {}
            """
        And we get "/archive/item-1"
        Then item "item-1" is unlocked
