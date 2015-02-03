Feature: Archive Ingest

    @auth
    Scenario: Move item into archive - tag not on ingest
        Given empty "archive"
		And empty "ingest"
        When we post to "/archive_ingest"
        """
        {
        "guid": "not_on_ingest_tag"
        }
        """
        Then we get error 404
		"""
		{"_message": "Fail to found ingest item with guid: not_on_ingest_tag", "_status": "ERR"}
		"""


    @auth
    Scenario: Move item into archive - no provider
        Given empty "archive"
        And "ingest"
        """
        [{"guid": "tag:reuters.com,0000:newsml_GM1EA6A1P8401", "state": "ingested"}]
        """
        When we post to "/archive_ingest"
        """
        {
        "guid": "tag:reuters.com,0000:newsml_GM1EA6A1P8401"
        }
        """
        Then we get archive ingest result
        """
        {"state": "FAILURE",  "error": "For ingest with guid= tag:reuters.com,0000:newsml_GM1EA6A1P8401, failed to retrieve provider with _id=None"}
        """

    @auth
    @provider
    Scenario: Move item into archive - success
        Given empty "archive"
    	When we fetch from "reuters" ingest "tag:reuters.com,0000:newsml_GM1EA7M13RP01"
        When we post to "/archive_ingest" with success
        """
        {
        "guid": "tag:reuters.com,0000:newsml_GM1EA7M13RP01"
        }
        """
        And we get "/archive/tag:reuters.com,0000:newsml_GM1EA7M13RP01"
        Then we get existing resource
		"""
        {
            "renditions": {
                "baseImage": {"height": 845, "mimetype": "image/jpeg", "width": 1400},
                "original": {"height": 2113, "mimetype": "image/jpeg", "width": 3500},
                "thumbnail": {"height": 120, "mimetype": "image/jpeg", "width": 198},
                "viewImage": {"height": 386, "mimetype": "image/jpeg", "width": 640}
            }
        }
  		"""

    @auth
    @provider
    Scenario: Move package into archive - check items
    	Given empty "ingest"
    	When we fetch from "reuters" ingest "tag:reuters.com,2014:newsml_KBN0FL0NM"
        And we post to "/archive_ingest"
        """
        {
        "guid": "tag:reuters.com,2014:newsml_KBN0FL0NM"
        }
        """
		And we get "/archive"
        Then we get existing resource
		"""
		{
            "_items": [
                {
                    "_version": 1,
                    "guid": "tag:reuters.com,2014:newsml_LYNXMPEA6F0MS",
                    "linked_in_packages": [{"package": "tag:reuters.com,2014:newsml_KBN0FL0NM"}],
                    "state": "fetched",
                    "type": "picture"
                },
                {
                    "_version": 1,
                    "groups": [
                        {
                            "refs": [
                                {"itemClass": "icls:text", "residRef": "tag:reuters.com,2014:newsml_KBN0FL0NN"},
                                {"itemClass": "icls:picture", "residRef": "tag:reuters.com,2014:newsml_LYNXMPEA6F13M"},
                                {"itemClass": "icls:picture", "residRef": "tag:reuters.com,2014:newsml_LYNXMPEA6F0MS"},
                                {"itemClass": "icls:picture", "residRef": "tag:reuters.com,2014:newsml_LYNXMPEA6F0MT"}
                            ]
                        },
                        {"refs": [{"itemClass": "icls:text", "residRef": "tag:reuters.com,2014:newsml_KBN0FL0ZP"}]}
                    ],
                    "guid": "tag:reuters.com,2014:newsml_KBN0FL0NM",
                    "state": "fetched",
                    "type": "composite"
                },
                {
                    "_version": 1,
                    "guid": "tag:reuters.com,2014:newsml_LYNXMPEA6F0MT",
                    "linked_in_packages": [{"package": "tag:reuters.com,2014:newsml_KBN0FL0NM"}],
                    "state": "fetched",
                    "type": "picture"
                },
                {
                    "_version": 1,
                    "guid": "tag:reuters.com,2014:newsml_KBN0FL0ZP",
                    "linked_in_packages": [{"package": "tag:reuters.com,2014:newsml_KBN0FL0NM"}],
                    "state": "fetched",
                    "type": "text"
                },
                {
                    "_version": 1,
                    "guid": "tag:reuters.com,2014:newsml_LYNXMPEA6F13M",
                    "linked_in_packages": [{"package": "tag:reuters.com,2014:newsml_KBN0FL0NM"}],
                    "state": "fetched",
                    "type": "picture"
                },
                {
                    "_version": 1,
                    "guid": "tag:reuters.com,2014:newsml_KBN0FL0NN",
                    "linked_in_packages": [{"package": "tag:reuters.com,2014:newsml_KBN0FL0NM"}],
                    "state": "fetched",
                    "type": "text"
                }
            ]
        }
		"""

    @auth
    @provider
    Scenario: Fetch item into specific desk
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
        Then we get new resource
        When we get "/archive?q=#desks._id#"
        Then we get list with 1 items

    @auth
    @provider
    Scenario: Fetched item should have "in_progress" state when locked and edited
        Given empty "archive"
        And "desks"
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
        And we post to "/archive/tag:reuters.com,2014:newsml_LOVEA6M0L7U2E/lock"
        """
        {}
        """
        And we patch "/archive/tag:reuters.com,2014:newsml_LOVEA6M0L7U2E"
        """
        {"headline": "test 2"}
        """
        Then we get existing resource
        """
        {"headline": "test 2", "state": "in_progress", "task": {"desk": "#desks._id#"}}
        """
