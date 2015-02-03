Feature: Duplication

    @auth
    @provider
    Scenario: Fetch same ingest item to a desk twice
        Given empty "archive"
        Given "desks"
            """
            [{"name": "Sports"}]
            """
        And ingest from "reuters"
            """
            [{"guid": "tag:reuters.com,2014:newsml_LOVEA6M0L7U2E"}]
            """
        When we post to "/archive_ingest"
            """
            {"guid": "tag:reuters.com,2014:newsml_LOVEA6M0L7U2E", "desk": "#desks._id#"}
            """
        And we post to "/archive_ingest"
            """
            {"guid": "tag:reuters.com,2014:newsml_LOVEA6M0L7U2E", "desk": "#desks._id#"}
            """
        Then we get new resource
        When we get "/archive?q=#desks._id#"
        Then we get list with 2 items

    @auth
    @provider
    Scenario: Fetch ingest item to a desk with ingest and family ids
        Given empty "archive"
        Given "desks"
            """
            [{"name": "Sports"}]
            """
        And ingest from "reuters"
            """
            [{"guid": "tag:reuters.com,2014:newsml_LOVEA6M0L7U2E"}]
            """
        And we post to "/archive_ingest"
            """
            {"guid": "tag:reuters.com,2014:newsml_LOVEA6M0L7U2E", "desk": "#desks._id#"}
            """
        And we get "/archive"
        Then we get existing resource
        Then we get "family_id" populated
        Then we get "ingest_id" populated

    @auth
    @provider
    Scenario: Fetch ingest item twice with same family ids
        Given empty "archive"
        Given "desks"
            """
            [{"name": "Sports"}]
            """
        And ingest from "reuters"
            """
            [{"guid": "tag:reuters.com,2014:newsml_LOVEA6M0L7U2E"}]
            """
        And we post to "/archive_ingest"
            """
            {"guid": "tag:reuters.com,2014:newsml_LOVEA6M0L7U2E", "desk": "#desks._id#"}
            """
        And we get "/archive"
        Then we get existing resource
        Then we get "family_id"
        And we post to "/archive_ingest"
            """
            {"guid": "tag:reuters.com,2014:newsml_LOVEA6M0L7U2E", "desk": "#desks._id#"}
            """
        When we get "/archive?q=#desks._id#"
        Then we get list with 2 items
        """
        {"_items": [
        		{"family_id": "#family_id"},
        		{"family_id": "#family_id"}
        """

    @auth
    Scenario: Duplicate a content item on the same desk
        Given "desks"
        """
        [{"name": "Sports"}]
        """
        Given "archive"
        """
        [{"guid": "tag:example.com,0000:newsml_BRE9A605"}]
        """
        And we post to "/archive_ingest"
        """
        {"guid": "tag:example.com,0000:newsml_BRE9A605", "desk": "#desks._id#"}
        """

        When we get "/archive?q=#desks._id#"
        Then we get list with 2 items

    @auth
    Scenario: Duplicate a content with history for a submitted item
        Given "desks"
        """
        [{"name": "Sports"}]
        """
        Given the "archive"
	    """
        [{"type":"text", "headline": "test1", "guid": "123", "original_creator": "abc", "state": "submitted"}]
        """
        And we get "/archive"
        Then we get existing resource
        Then we get "family_id"
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
       	When we get "/archive/123?version=all"
        Then we get list with 3 items
        And we post to "/archive_ingest"
        """
        {"guid": "tag:example.com,0000:newsml_BRE9A605", "desk": "#desks._id#"}
        """

        When we get "guid"
        Then we get "/archive/#guid?version=all"
        Then we get list with 3 items

    @auth
    Scenario: Duplicate a content with history for a non-submitted item
        Given "desks"
        """
        [{"name": "Sports"}]
        """
        Given the "archive"
	    """
        [{"type":"text", "headline": "test1", "guid": "123", "original_creator": "abc", "state": "in-progress"}]
        """
        And we get "/archive"
        Then we get existing resource
        Then we get "family_id"
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
       	When we get "/archive/123?version=all"
        Then we get list with 3 items
        And we post to "/archive_ingest"
        """
        {"guid": "tag:example.com,0000:newsml_BRE9A605", "desk": "#desks._id#"}
        """

        When we get "guid"
        Then we get "/archive/#guid?version=all"
        Then we get list with 4 items

    @auth
    Scenario: Duplicated versions are identical

    @auth
    Scenario: Duplicated item fields are identical

    @auth
    Scenario: Create a new archive item with family id populated

    @auth
    Scenario: Search the duplicated items
    - search with family_id:xxx to return all related items