Feature: News Items Archive

    @auth
    Scenario: List empty archive
        Given empty "archive"
        When we get "/archive"
        Then we get list with 0 items

    @auth
    Scenario: Move item into archive
        Given empty "archive"
        And "ingest"
            """
            [{"guid": "tag:xyz-abc-123", "headline": "htext"}]
            """

        When we post to "/archive"
            """
            {
                "uri": "tag:xyz-abc-123",
                "guid": "tag:xyz-abc-123",
                "headline": "htext",
                "urgency": "3",
                "firstcreated": "2013-11-07T13:54:45+00:00",
                "versioncreated": "2013-11-07T13:54:45+00:00",
                "type": "text"
            }
            """

        Then we get new resource
            """
            {"_id": "tag:xyz-abc-123", "guid": "tag:xyz-abc-123", "headline": "htext"}
            """
        And we get "archived" in "ingest/tag:xyz-abc-123"

    @auth
    Scenario: Get archive item by guid
        Given "archive"
            """
            [{"guid": "tag:example.com,0000:newsml_BRE9A605"}]
            """

        When we get "/archive/tag:example.com,0000:newsml_BRE9A605"
        Then we get existing resource
            """
            {"guid": "tag:example.com,0000:newsml_BRE9A605"}
            """

    @auth
    Scenario: Update item
        Given "archive"
            """
            [{"_id": "xyz", "guid": "testid", "headline": "test"}]
            """

        When we patch "/archive/xyz"
            """
            {"slugline": "TEST", "urgency": 2, "version": "1"}
            """

        And we patch again
            """
            {"slugline": "TEST2", "version": "2"}
            """

        Then we get updated response
        And we get etag matching "/archive/xyz"
