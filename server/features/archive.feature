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
        {"guid": "tag:example.com,0000:newsml_BRE9A605", "state": "draft"}
        """

    @auth
    Scenario: Don't get published archive item by guid
        Given "archive"
        """
        [{"guid": "tag:example.com,0000:newsml_BRE9A605", "state": "published"}]
        """

        When we get "/archive"
        Then we get list with 0 items

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
        {"headline": "TEST 3", "state": "in_progress", "body_html": "<p>some content</p>"}
        """

        Then we get updated response
        """
        {"word_count": 2, "operation": "update"}
        """
        And we get version 3
        And we get etag matching "/archive/xyz"

        When we get "/archive/xyz?version=all"
        Then we get list with 3 items

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
        {"headline": "another one", "state": "in_progress"}
        """

        And we get "archive/item-1"
        Then we get global content expiry
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
        Then we get updated response
        """
        {"operation": "restore"}
        """
        And we get version 3
        And we get global content expiry
        And the field "headline" value is "test"


    @auth
    Scenario: Upload image into archive
        Given empty "archive"
        When we upload a file "bike.jpg" to "archive"
        Then we get new resource
        """
        {"guid": "__any_value__", "firstcreated": "__any_value__", "versioncreated": "__any_value__", "state": "draft"}
        """
        And we get "bike.jpg" metadata
        And we get "picture" renditions
        When we patch latest
        """
        {"headline": "flower", "byline": "foo", "description": "flower desc"}
        """
        When we get "/archive"
        Then we get list with 1 items
        """
        {"_items": [{"headline": "flower", "byline": "foo", "description": "flower desc",
                     "pubstatus": "usable", "language": "en", "state": "draft"}]}
        """

    @auth
    Scenario: Upload audio file into archive
        Given empty "archive"
        When we upload a file "green.ogg" to "archive"
        Then we get new resource
        """
        {"guid": "__any_value__", "state": "draft"}
        """
        And we get "green.ogg" metadata
        Then original rendition is updated with link to file having mimetype "audio/ogg"
        When we patch latest
        """
        {"headline": "green", "byline": "foo", "description": "green music"}
        """
        When we get "/archive"
        Then we get list with 1 items
        """
        {"_items": [{"headline": "green", "byline": "foo", "description": "green music", "state": "draft"}]}
        """

    @auth
    Scenario: Upload video file into archive
        Given empty "archive"
        When we upload a file "this_week_nasa.mp4" to "archive"
        Then we get new resource
        """
        {"guid": "__any_value__", "state": "draft"}
        """
        And we get "this_week_nasa.mp4" metadata
        Then original rendition is updated with link to file having mimetype "video/mp4"
        When we patch latest
        """
        {"headline": "week @ nasa", "byline": "foo", "description": "nasa video"}
        """
        When we get "/archive"
        Then we get list with 1 items
        """
        {"_items": [{"headline": "week @ nasa", "byline": "foo", "description": "nasa video", "state": "draft"}]}
        """

    @auth
    Scenario: Browse private content
        Given the "archive"
        """
        [{"type":"text", "headline": "test1", "guid": "testid1"},
         {"type":"text", "headline": "test2", "guid": "testid2"}]
        """
        When we get "/archive"
        Then we get list with 0 items

    @auth
    Scenario: Browse public content
        Given "desks"
        """
        [{"name": "Sports Desk", "spike_expiry": 60}]
        """
        Given "archive"
            """
            [{"_id": "testid1", "guid": "testid1", "task": {"desk": "#desks._id#"}}]
            """
        When we get "/archive"
        Then we get list with 1 items

        When we get "archive/testid1"
        Then we get global content expiry

    @auth
    @ticket-sd-360
    Scenario: Delete archive item with guid starting with "-"
        Given empty "archive"
        When we post to "/archive"
        """
        [{"guid": "-abcde1234567890", "type": "text"}]
        """
        And we delete latest
        Then we get response code 405

    @auth
    Scenario: Create new text item
        Given empty "archive"
        When we post to "/archive"
        """
        [{"type": "text", "body_html": "<p>content</p>"}]
        """
        Then we get new resource
        """
        {
        	"_id": "__any_value__", "guid": "__any_value__", "type": "text",
        	"original_creator": "__any_value__", "word_count": 1, "operation": "create"
        }
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
        {"headline": "test3", "version_creator": "#user._id#"}
        """
       	And we get version 3
       	When we get "/archive/xyz?version=all"
        Then we get list with 3 items

	@auth
	Scenario: Update text item with Metadata
	    Given the "archive"
	    """
        [{"type":"text", "headline": "test1", "_id": "xyz", "original_creator": "abc"}]
        """
        When we patch given
        """
        {"word_count" : "6", "keywords" : ["Test"], "urgency" : "4", "byline" : "By Line", "language": "en", "genre" : [{"name": "Test"}],
         "anpa_category" : [{"qcode" : "A", "name" : "Australian News"}],
         "subject" : [{"qcode" : "11007000", "name" : "human rights"},
                      {"qcode" : "11014000", "name" : "treaty and international organisation-DEPRECATED"}
                     ]
        }
        """
        Then we get updated response
        """
        { "headline": "test1", "pubstatus" : "usable", "byline" : "By Line", "genre": [{"name": "Test"}]}
        """
        And we get version 2

	@auth
	Scenario: Unique Name should be unique
	    Given the "archive"
	    """
        [{"type":"text", "headline": "test1", "_id": "xyz", "original_creator": "abc"},
         {"type":"text", "headline": "test1", "_id": "abc", "original_creator": "abc"}]
        """
        When we patch "/archive/xyz"
        """
        {"unique_name": "unique_xyz"}
        """
        And we patch "/archive/abc"
        """
        {"unique_name": "unique_xyz"}
        """
        Then we get response code 400

	@auth
	Scenario: Unique Name can be updated by administrator
	    Given the "archive"
	    """
        [{"type":"text", "headline": "test1", "_id": "xyz", "original_creator": "abc"},
         {"type":"text", "headline": "test1", "_id": "abc", "original_creator": "abc"}]
        """
        When we patch "/archive/xyz"
        """
        {"unique_name": "unique_xyz"}
        """
        Then we get response code 200

	@auth
	Scenario: Unique Name can be updated only by user having privileges
	    Given the "archive"
	    """
        [{"type":"text", "headline": "test1", "_id": "xyz", "original_creator": "abc"},
         {"type":"text", "headline": "test1", "_id": "abc", "original_creator": "abc"}]
        """
        When we patch "/users/#CONTEXT_USER_ID#"
        """
        {"user_type": "user", "privileges": {"metadata_uniquename": 0, "archive": 1, "unlock": 1, "tasks": 1, "users": 1}}
        """
        Then we get response code 200
        When we patch "/archive/xyz"
        """
        {"unique_name": "unique_xyz"}
        """
        Then we get response code 400
        When we setup test user
        When we patch "/users/#CONTEXT_USER_ID#"
        """
        {"user_type": "user", "privileges": {"metadata_uniquename": 1, "archive": 1, "unlock": 1, "tasks": 1, "users": 1}}
        """
        Then we get response code 200
        When we patch "/archive/xyz"
        """
        {"unique_name": "unique_xyz"}
        """
        Then we get response code 200

    @auth
    Scenario: State of an Uploaded Image, submitted to a desk when updated should change to in-progress
        Given empty "archive"
        And "desks"
        """
        [{"name": "Sports"}]
        """
        When we upload a file "bike.jpg" to "archive"
        Then we get new resource
        """
        {"guid": "__any_value__", "firstcreated": "__any_value__", "versioncreated": "__any_value__", "state": "draft"}
        """
        When we patch latest
        """
        {"headline": "flower", "byline": "foo", "description": "flower desc"}
        """
        When we get "/archive"
        Then we get list with 1 items
        """
        {"_items": [{"headline": "flower", "byline": "foo", "description": "flower desc",
                     "pubstatus": "usable", "language": "en", "state": "draft"}]}
        """
        When we patch "/archive/#archive._id#"
        """
        {"task": {"desk": "#desks._id#"}}
        """
        And we patch "/archive/#archive._id#"
        """
        {"headline": "FLOWER"}
        """
        And we get "/archive"
        Then we get list with 1 items
        """
        {"_items": [{"state": "in_progress"}]}
        """

    @auth
    Scenario: Cannot delete desk when it has article(s)
      Given empty "desks"
      And empty "archive"
      When we post to "/desks"
      """
      {"name": "Sports"}
      """
      And we post to "/archive"
      """
      [{"type": "text", "body_html": "<p>content</p>", "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]
      """
      And we delete "/desks/#desks._id#"
      Then we get error 412
      """
      {"_message": "Cannot delete desk as it has article(s)."}
      """

    @auth @test
    Scenario: Sign-off is properly updated
        When we post to "/archive"
        """
        [{"type": "text", "body_html": "<p>content</p>"}]
        """
        Then we get new resource
        """
        {"type": "text", "sign_off":"abc"}
        """
        When we patch latest
        """
        {"headline": "test3"}
        """
        Then we get updated response
        """
        {"headline": "test3", "sign_off": "abc"}
        """
        When we switch user
        And we patch latest
        """
        {"headline": "test4"}
        """
        Then we get updated response
        """
        {"headline": "test4", "sign_off": "abc/foo"}
        """

    @auth
    Scenario: Assign a default Source to user created content Items
        When we post to "/archive"
        """
        [{"type": "text", "body_html": "<p>content</p>"}]
        """
        Then we get new resource
        """
        {"type": "text", "source":"AAP"}
        """

    @auth
    Scenario: Dateline is populated from user preferences for new articles
      Given empty "archive"
      And we have sessions "/sessions"
      When we get "/preferences/#SESSION_ID#"
      And we patch latest
      """
      {"user_preferences": {"dateline:located": {
          "located" : {
              "dateline" : "city", "city" : "Sydney", "city_code" : "Sydney", "country" : "Australia", "country_code" : "AU",
              "state" : "New South Wales", "state_code" : "NSW", "tz" : "Australia/Sydney", "alt_name": ""
          }}}}
      """
      And we post to "/archive"
      """
      [{"headline": "Article with Dateline populated from preferences"}]
      """
      Then we get latest
      """
      {"dateline": {"located": {"city": "Sydney"}}}
      """