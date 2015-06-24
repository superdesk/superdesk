Feature: AAP Multimedia Feature

    @auth
    Scenario: Can search multimedia
        Given "ingest_providers"
	    """
        [{
            "config": {"password":"", "username":""},
            "is_closed": false,
            "name": "AAP One",
            "source": "aapmm",
            "type": "search"
        }]
	    """
        When we get "/aapmm"
        Then we get list with +1 items

    @auth
    Scenario: Can search fetch from
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
        Then we get response code 201

