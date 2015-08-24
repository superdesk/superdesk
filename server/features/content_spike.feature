Feature: Content Spiking

    @auth
    Scenario: Spike a user content and validate metadata set by API
        Given "archive"
        """
        [{"_id": "item-1", "guid": "item-1", "headline": "test", "_current_version": 1, "state": "draft"}]
        """
        When we get "/archive/item-1"
        Then we get latest
        """
        {"_id": "item-1", "state": "draft", "sign_off": "abc"}
        """
        When we spike "item-1"
        Then we get OK response
        And we get spiked content "item-1"
        And we get version 2
        And we get global spike expiry
        When we get "/archive/item-1"
        Then we get existing resource
        """
        {"_id": "item-1", "state": "spiked", "sign_off": "abc"}
        """

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
        [{"_id": "item-1", "guid": "item-1", "_current_version": 1, "headline": "test", "task":{"desk":"#desks._id#", "stage" :"#desks.incoming_stage#"}}]
        """
        When we spike "item-1"
        Then we get OK response
        And we get spiked content "item-1"
        And we get version 2
        And we get desk spike expiry after "60"
        When we get "/archive/item-1"
        Then we get existing resource
        """
        {"_id": "item-1", "state": "spiked", "sign_off": "abc"}
        """

    @auth
    @provider
    Scenario: Spike fetched content
        Given empty "archive"
        Given "desks"
        """
        [{"name": "Sports Desk"}]
        """
        And ingest from "reuters"
        """
        [{"guid": "tag:reuters.com,2014:newsml_LOVEA6M0L7U2E"}]
        """
        When we post to "/ingest/tag:reuters.com,2014:newsml_LOVEA6M0L7U2E/fetch"
        """
        {"desk": "#desks._id#"}
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
        [{"_id": "item-1", "guid": "item-1", "_current_version": 1, "headline": "test", "state": "draft"}]
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
        [{"_id": "item-1", "guid": "item-1", "_current_version": 1, "headline": "test", "task":{"desk":"#desks._id#", "stage" :"#desks.incoming_stage#"}}]
        """
        When we spike "item-1"
        And we unspike "item-1"
        Then we get unspiked content "item-1"
        And we get version 3
        And we get global content expiry

    @auth
    Scenario: Sign Off changes when content is spiked or unspiked
        Given "desks"
        """
        [{"name": "Sports Desk", "spike_expiry": 60}]
        """
        When we post to "/archive" with success
        """
        [{"guid": "item-1", "headline": "test", "task":{"desk":"#desks._id#", "stage" :"#desks.incoming_stage#"}}]
        """
        Then we get new resource
        """
        {"sign_off": "abc"}
        """
        When we switch user
        And we spike "#archive._id#"
        Then we get OK response
        When we get "/archive/#archive._id#"
        Then we get existing resource
        """
        {"sign_off": "abc/foo"}
        """
        When we login as user "bar" with password "foobar" and user type "admin"
        """
        {"sign_off": "bar"}
        """
        And we unspike "#archive._id#"
        Then we get OK response
        When we get "/archive/#archive._id#"
        Then we get existing resource
        """
        {"sign_off": "abc/foo/bar"}
        """
