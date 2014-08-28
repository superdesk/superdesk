Feature: News Items Archive

    @auth
    Scenario: List empty archive
        Given empty "archive"
        When we get "/archive"
        Then we get list with 0 items

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
        {"headline": "TEST 2", "urgency": 2}
        """

        And we patch latest
        """
        {"headline": "TEST 3"}
        """

        Then we get updated response
        And we get version 3
        And we get etag matching "/archive/xyz"

        When we get "/archive/xyz?version=all"
        Then we get list with 3 items

    @wip
    @auth
    Scenario: Update item and keep version
        Given "archive"
        """
        [{"_id": "item-1", "guid": "item-1", "headline": "test"}]
        """

        When we patch given
        """
        {"headline": "another"}
        """

        And we post to "archive/item-1/autosave"
        """
        {"headline": "another one"}
        """

        And we get "archive/item-1"
        Then we get version 2

	@auth
	Scenario: Restore version
        Given "archive"
        """
        [{"guid": "testid", "headline": "test"}]
        """
        When we patch given
        """
        {"headline": "TEST 2", "urgency": 2}
        """
		And we restore version 1

        Then we get version 3
        And the field "headline" value is "test"


    @wip
    @auth
    Scenario: Upload image into archive
        Given empty "archive"
        When we upload a file "bike.jpg" to "archive_media"
        Then we get new resource
        """
        {"guid": "", "firstcreated": "", "versioncreated": ""}
        """
        And we get "bike.jpg" metadata
        And we get "picture" renditions

        When we patch latest
        """
        {"headline": "flower", "byline": "foo", "description_text": "flower desc"}
        """

        When we get "/archive"
        Then we get list with 1 items
        """
        {"_items": [{"headline": "flower", "byline": "foo", "description_text": "flower desc"}]}
        """

    @auth
    Scenario: Upload audio file into archive
        Given empty "archive"
        When we upload a file "green.ogg" to "archive_media"
        Then we get new resource
        """
        {"guid": ""}
        """
        And we get "green.ogg" metadata
        Then original rendition is updated with link to file having mimetype "audio/ogg"
        When we patch latest
        """
        {"headline": "green", "byline": "foo", "description_text": "green music"}
        """
        When we get "/archive"
        Then we get list with 1 items
        """
        {"_items": [{"headline": "green", "byline": "foo", "description_text": "green music"}]}
        """

    @auth
    Scenario: Upload video file into archive
        Given empty "archive"
        When we upload a file "this_week_nasa.mp4" to "archive_media"
        Then we get new resource
        """
        {"guid": ""}
        """
        And we get "this_week_nasa.mp4" metadata
        Then original rendition is updated with link to file having mimetype "video/mp4"
        When we patch latest
        """
        {"headline": "week @ nasa", "byline": "foo", "description_text": "nasa video"}
        """
        When we get "/archive"
        Then we get list with 1 items
        """
        {"_items": [{"headline": "week @ nasa", "byline": "foo", "description_text": "nasa video"}]}
        """

    @auth
    Scenario: Cancel audio upload
        Given empty "archive"
        When we upload a file "green.ogg" to "archive_media"
        And we delete latest
        Then we get deleted response

    @auth
    Scenario: Cancel upload
        Given empty "archive"
        When we upload a file "bike.jpg" to "archive_media"
        And we delete latest
        Then we get deleted response

    @auth
    Scenario: Browse content
        Given the "archive"
        """
        [{"type":"text", "headline": "test1", "guid": "testid1", "original_creator": "abc"}, {"type":"text", "headline": "test2", "guid": "testid2", "original_creator": "abc"}]
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
        {"_id": "", "guid": "", "type": "text", "original_creator": ""}
        """

	@auth
	Scenario: Update text items
	    Given the "archive"
	    """
        [{"type":"text", "headline": "test1", "_id": "xyz", "original_creator": "abc"}]
        """
        When we switch user
        When we patch given
        """
        {"headline": "test2"}
        """
        And we patch latest
        """
        {"headline": "test3"}
        """
        Then we get updated response
        """
        {"headline": "test3", "version_creator":"def"}
        """
       	And we get version 3
       	When we get "/archive/xyz?version=all"
        Then we get list with 3 items
