Feature: Legal Archive

    @auth
    Scenario: Create legal archive item
        Given empty "legal_archive"
        Given empty "archive"

        When we post to "/archive"
            """
            {"guid": "item-1", "headline": "test"}
            """

        Then we get existing resource
            """
            {"guid": "item-1", "headline": "test"}
            """

        When we get "/legal_archive/item-1"
        Then we get existing resource
            """
            {"guid": "item-1", "headline": "test"}
            """

    @auth
    Scenario: Update legal archive item
        Given "legal_archive"
            """
            [{"_id": "item-1", "guid": "item-1", "headline": "test"}]
            """
        Given "archive"
            """
            [{"_id": "item-1", "guid": "item-1", "headline": "test"}]
            """

        When we patch "/archive/item-1"
            """
            {"guid": "item-1", "headline": "test2"}
            """
        Then we get OK response

        When we get "/legal_archive/item-1"
        Then we get existing resource
            """
            {"guid": "item-1", "headline": "test2"}
            """
