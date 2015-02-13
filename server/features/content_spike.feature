Feature: Content Spiking

    @auth
    Scenario: Spike a user content
        Given empty "archive"
        Given "archive"
            """
            [{"_id": "item-1", "guid": "item-1", "headline": "test", "_version": 1, "state": "draft"}]
            """

        When we spike "item-1"
        Then we get OK response
        And we get spiked content "item-1"
        And we get version 2
        And we get global spike expiry

    @auth
    Scenario: Spike a desk content
        Given empty "desks"
        Given empty "archive"
        Given empty "stages"
        Given "desks"
        """
        [{"name": "Sports Desk", "spike_expiry": 60}]
        """
        Given "archive"
        """
        [{"_id": "item-1", "guid": "item-1", "_version": 1, "headline": "test", "task":{"desk":"#desks._id#", "stage" :"#desks.incoming_stage#"}}]
        """
        When we spike "item-1"
        Then we get OK response
        And we get spiked content "item-1"
        And we get version 2
        And we get desk spike expiry after "60"

    @auth
    @provider
    Scenario: Spike fetched content
        Given empty "archive"
        And ingest from "reuters"
            """
            [{"guid": "tag:reuters.com,2014:newsml_LOVEA6M0L7U2E"}]
            """
        When we post to "/archive_ingest"
            """
            {"guid": "tag:reuters.com,2014:newsml_LOVEA6M0L7U2E"}
            """
        Then we get "_id"
        When we spike fetched item
        """
        {"_id": "#_id#"}
        """
        Then we get OK response

    @auth
    Scenario: Unspike a content
        Given empty "archive"
        Given we have "administrator" as type of user
        Given "archive"
            """
            [{"_id": "item-1", "guid": "item-1", "_version": 1, "headline": "test", "state": "draft"}]
            """

        When we spike "item-1"
        And we unspike "item-1"
        Then we get unspiked content "item-1"
        And we get version 3
        And we get global content expiry

    @auth
    Scenario: Unspike a desk content
        Given empty "desks"
        Given empty "archive"
        Given empty "stages"
        Given "desks"
        """
        [{"name": "Sports Desk", "spike_expiry": 60}]
        """
        Given "archive"
        """
        [{"_id": "item-1", "guid": "item-1", "_version": 1, "headline": "test", "task":{"desk":"#desks._id#", "stage" :"#desks.incoming_stage#"}}]
        """
        When we spike "item-1"
        And we unspike "item-1"
        Then we get unspiked content "item-1"
        And we get version 3
        And we get global content expiry