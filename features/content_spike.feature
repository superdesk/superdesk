Feature: Content Spiking

    @auth
    Scenario: spike a user content
        Given empty "archive"
        Given "archive"
            """
            [{"_id": "item-1", "guid": "item-1", "headline": "test"}]
            """

        When we post to "/archive/item-1/spike"
            """
            {"is_spiked": true}
            """
        Then we get OK response
        Then we get spiked content "item-1"
        Then we get global spike expiry


    @auth
    Scenario: spike a desk content
        Given empty "desks"
        Given empty "archive"
        Given empty "stages"
        When we post to "/stages"
            """
            {
            "name": "show my content",
            "description": "Show content items created by the current logged user"
            }
            """
        When we post to "desks"
            """
            {"name": "Sports Desk", "incoming_stage": "#STAGES_ID#", "spike_expiry": 60}
            """
        Given "archive"
            """
            [{"_id": "item-1", "guid": "item-1", "headline": "test", "task":{"desk":"#DESKS_ID#", "stage" :"#STAGES_ID#"}}]
            """
        When we post to "/archive/item-1/spike"
            """
            {"is_spiked": true}
            """
        Then we get OK response
        Then we get spiked content "item-1"
        Then we get desk spike expiry after "60"


    @auth
    Scenario: unspike a content
        Given empty "archive"
        Given we have "administrator" as type of user
        Given "archive"
            """
            [{"_id": "item-1", "guid": "item-1", "headline": "test"}]
            """

        When we post to "/archive/item-1/spike"
            """
            {"is_spiked": true}
            """
        Then we get OK response

        When we unspike "/archive/item-1"

        Then we get unspiked content "item-1"
