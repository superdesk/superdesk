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

        When we post to "/archive_ingest"
            """
            {
                "guid": "tag:xyz-abc-123"
            }
            """

        Then we get new resource
            """
            {"guid": "tag:xyz-abc-123"}
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

    @auth
    Scenario: Upload file into archive
        Given empty "archive"
        When we upload a binary file to "archive_media"
        Then we get new resource
            """
            {"guid": ""}
            """
        And we get file metadata

        When we patch again
            """
            {"headline": "flower", "byline": "foo", "description_text": "flower desc"}
            """

        When we get "/archive"
        Then we get list with 1 items
            """
            {"headline": "flower", "byline": "foo", "description_text": "flower desc"}
            """

    @auth
    Scenario: Upload file into archive and import baseImage rendition
        Given empty "archive"
        When we upload a binary file to "archive_media"
        Then we get new resource
            """
            {"guid": ""}
            """
        And we get file metadata
        When we import rendition from url
        When we get updated media from archive
        Then baseImage rendition is updated

    @auth
    Scenario: Upload file into archive and import renditions
        Given empty "archive"
        When we upload a binary file to "archive_media"
        Then we get new resource
            """
            {"guid": ""}
            """
        And we get file metadata
        When we import thumbnail rendition from url
        When we get updated media from archive
        Then thumbnail rendition is updated

    @wip
    @auth
    Scenario: Cancel upload
        Given empty "archive"
        When we upload a binary file to "archive_media"
        And we delete it
        Then we get deleted response

	@auth
	Scenario: Browse content
		Given "archive"
			"""
            [{"type":"text", "headline": "test1", "guid": "testid1"}, {"type":"text", "headline": "test2", "guid": "testid2"}]
            """		
		When we get "/archive"
        Then we get list with 2 items
