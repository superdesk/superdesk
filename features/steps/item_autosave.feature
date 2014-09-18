@wip
Feature: Content Autosave

    @auth
    Scenario: Autosave item
        Given empty "archive_autosave"
        Given "archive"
            """
            [{"_id": "item-1", "guid": "item-1", "headline": "test"}]
            """

        When we post to "/archive_autosave"
            """
            {"_id": "item-1", "guid": "item-1", "headline": "test"}
            """
        Then we get existing resource
            """
            {"_id": "item-1", "guid": "item-1", "headline": "test"}
            """

    @auth
    Scenario: Autosave does not accept invalid item
        Given empty "archive"
        Given empty "archive_autosave"
        When we post to "/archive_autosave"
            """
            {"_id": "item-1", "guid": "item-1", "headline": "test"}
            """
        Then we get error 404

    @auth
    Scenario: Clean autosave on locked item
        Given empty "archive_autosave"
        Given "archive"
            """
            [{"_id": "item-1", "guid": "item-1", "headline": "test"}]
            """

        When we post to "/archive_autosave"
            """
            {"_id": "item-1", "guid": "item-1", "headline": "test"}
            """
        Then we get existing resource
            """
            {"_id": "item-1", "guid": "item-1", "headline": "test"}
            """

        When we post to "/archive/item-1/lock"
            """
            {}
            """
        Then item "item-1" is locked

        When we get "/archive_autosave/item-1"
        Then we get error 404

    @auth
    Scenario: Clean autosave on item save
        Given empty "archive_autosave"
        Given "archive"
            """
            [{"_id": "item-1", "guid": "item-1", "headline": "test"}]
            """

        When we post to "/archive_autosave"
            """
            {"_id": "item-1", "guid": "item-1", "headline": "test"}
            """
        Then we get existing resource
            """
            {"_id": "item-1", "guid": "item-1", "headline": "test"}
            """

        When we patch "/archive/item-1"
            """
            {"guid": "item-1", "headline": "test"}
            """
        Then we get OK response

        When we get "/archive_autosave/item-1"
        Then we get error 404
