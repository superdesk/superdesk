Feature: Content Spiking

    @auth
    Scenario: Spike a user content
        Given empty "archive"
        Given "archive"
            """
            [{"_id": "item-1", "guid": "item-1", "headline": "test", "state": "draft"}]
            """

        When we spike "item-1"
        Then we get OK response
        And we get spiked content "item-1"
        And we get global spike expiry


    @auth
    Scenario: Spike a desk content
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
        And we post to "desks"
            """
            {"name": "Sports Desk", "incoming_stage": "#STAGES_ID#", "spike_expiry": 60}
            """
        Given "archive"
            """
            [{"_id": "item-1", "guid": "item-1", "headline": "test", "task":{"desk":"#DESKS_ID#", "stage" :"#STAGES_ID#"}}]
            """
        When we spike "item-1"
        Then we get OK response
        And we get spiked content "item-1"
        And we get desk spike expiry after "60"

    @auth
    Scenario: Unspike a content
        Given empty "archive"
        Given we have "administrator" as type of user
        Given "archive"
            """
            [{"_id": "item-1", "guid": "item-1", "headline": "test", "state": "draft"}]
            """

        When we spike "item-1"
        And we unspike "item-1"
        Then we get unspiked content "item-1"
