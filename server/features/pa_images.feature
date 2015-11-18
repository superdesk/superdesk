Feature: PA Images

    @auth
    Scenario: Can search pa multimedia
        Given "ingest_providers"
	    """
        [{
            "config": {"password":"", "username":""},
            "is_closed": false,
            "name": "PA Images",
            "source": "paimg",
            "type": "search"
        }]
	    """
        When we get "/paimg"
        Then we get list with +1 items

    @auth
    Scenario: Can search fetch from pa images
        Given "desks"
        """
        [{"name": "Sports"}]
        """
        When we post to "/paimg"
        """
        {
        "guid": "2.24624700", "desk": "#desks._id#"
        }
        """
        Then we get response code 400

    @auth
    Scenario: Can search for last week
        Given "ingest_providers"
	    """
        [{
            "config": {"password":"", "username":""},
            "is_closed": false,
            "name": "PA Images",
            "source": "paimg",
            "type": "search"
        }]
	    """
        When we get "/paimg?source={"post_filter":{"and":[{"range":{"firstcreated":{"gte":"now-1w"}}}]},"query":{"filtered":{}},"size":48}"
        Then we get list with +1 items

    @auth
    Scenario: Can search for date range
        Given "ingest_providers"
	    """
        [{
            "config": {"password":"", "username":""},
            "is_closed": false,
            "name": "PA Images",
            "source": "paimg",
            "type": "search"
        }]
	    """
        When we get "/paimg?source={"post_filter":{"and":[{"range":{"firstcreated":{"lte":"2015-09-01T14:00:00+00:00","gte":"2015-08-31T14:00:00+00:00"}}}]},"query":{"filtered":{}},"size":48}"
        Then we get list with +1 items
