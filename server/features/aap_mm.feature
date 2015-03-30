Feature: AAP Multimedia Feature

    @auth
    Scenario: Can search multimedia
        When we get "/aapmm"
        Then we get list with +1 items

    @auth
    Scenario: Can search multimedia
        Given "desks"
        """
        [{"name": "Sports"}]
        """
        When we post to "/aapmm"
        """
        {
        "guid": "20150329001116807745", "desk": "#desks._id#"
        }
        """
