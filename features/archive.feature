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
        [{"guid": "tag:reuters.com,0000:newsml_GM1EA6A1P8401"}]
        """

        When we post to "/archive_ingest"
        """
        {
        "guid": "tag:reuters.com,0000:newsml_GM1EA6A1P8401"
        }
        """

        Then we get new resource
        """
        {"guid": "tag:reuters.com,0000:newsml_GM1EA6A1P8401"}
        """
        And we get "task_id"
        And we get "state" in "/archive_ingest/#task_id#"
        And we get "archived" in "ingest/tag:reuters.com,0000:newsml_GM1EA6A1P8401"
        

    @auth
    Scenario: Move item into archive - wrong guid
        Given empty "archive"
        And "ingest"
        """
        [{"guid": "tag:reuters.com,0000:newsml_GM1EA6A1P8401"}]
        """

        When we post to "/archive_ingest"
        """
        {
        "guid": "wrong guid"
        }
        """

        Then we get error 400
		"""
		{"_message": "", "_issues": "Fail to found ingest item with guid: wrong guid", "_status": "ERR"}
		"""


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

        When we patch given
        """
        {"slugline": "TEST", "urgency": 2, "version": "1"}
        """

        And we patch latest
        """
        {"slugline": "TEST2", "version": "2"}
        """

        Then we get updated response
        And we get etag matching "/archive/xyz"

    @auth
    Scenario: Upload image into archive
        Given empty "archive"
        When we upload a file "bike.jpg" to "archive_media"
        Then we get new resource
        """
        {"guid": ""}
        """
        And we get file metadata
        And we get image renditions

        When we patch latest
        """
        {"headline": "flower", "byline": "foo", "description_text": "flower desc"}
        """

        When we get "/archive"
        Then we get list with 1 items
        """
        {"headline": "flower", "byline": "foo", "description_text": "flower desc"}
        """

    @auth
    Scenario: Upload audio file into archive
        Given empty "archive"
        When we upload a file "green.ogg" to "archive_media"
        Then we get new resource
        """
        {"guid": ""}
        """
        Then original rendition is updated with link to file having mimetype "audio/ogg"
        When we patch latest
        """
        {"headline": "green", "byline": "foo", "description_text": "green music"}
        """
        When we get "/archive"
        Then we get list with 1 items
        """
        {"headline": "green", "byline": "foo", "description_text": "green music"}
        """

    @auth
    Scenario: Upload video file into archive
        Given empty "archive"
        When we upload a file "this_week_nasa.mp4" to "archive_media"
        Then we get new resource
        """
        {"guid": ""}
        """
        Then original rendition is updated with link to file having mimetype "video/mp4"
        When we patch latest
        """
        {"headline": "week @ nasa", "byline": "foo", "description_text": "nasa video"}
        """
        When we get "/archive"
        Then we get list with 1 items
        """
        {"headline": "week @ nasa", "byline": "foo", "description_text": "nasa video"}
        """


    @auth
    Scenario: Upload file into archive and import baseImage rendition
        Given empty "archive"
        When we upload a file "bike.jpg" to "archive_media"
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
        When we upload a file "bike.jpg" to "archive_media"
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
    Scenario: Cancel audio upload
        Given empty "archive"
        When we upload a file "green.ogg" to "archive_media"
        And we delete latest
        Then we get deleted response

    @wip
    @auth
    Scenario: Cancel upload
        Given empty "archive"
        When we upload a file "bike.jpg" to "archive_media"
        And we delete latest
        Then we get deleted response

    @auth
    Scenario: Browse content
        Given "archive"
        """
        [{"type":"text", "headline": "test1", "guid": "testid1"}, {"type":"text", "headline": "test2", "guid": "testid2"}]
        """
        When we get "/archive"
        Then we get list with 2 items

    @auth
    @ticket-sd-360
    Scenario: Delete archive item with guid starting with "-"
        Given empty "archive"
        When we post to "/archive"
        """
        [{"guid": "-abcde1234567890", "type": "text"}]
        """
        And we delete latest
        Then we get deleted response

    @auth
    Scenario: Create new text item
        Given empty "archive"
        When we post to "/archive"
        """
        [{"type": "text"}]
        """
        Then we get new resource
        """
        {"_id": "", "guid": "", "type": "text"}
        """
