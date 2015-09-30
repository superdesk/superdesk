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

    @auth
    Scenario: Can search credit and type facets
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
        When we get "/aapmm?source={"post_filter":{"and":[{"terms":{"type":["image"]}},{"terms":{"credit":["aapimage"]}}]},"query":{"filtered":{}},"size":48}"
        Then we get list with +1 items

    @auth
    Scenario: Can search categories facets
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
        When we get "/aapmm?source={"post_filter":{"and":[{"terms":{"anpa_category.name":["news"]}}]},"query":{"filtered":{}},"size":48}"
        Then we get list with +1 items

    @auth
    Scenario: Can search last week
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
        When we get "/aapmm?source={"post_filter":{"and":[{"range":{"firstcreated":{"gte":"now-1w"}}}]},"query":{"filtered":{}},"size":48}"
        Then we get list with +1 items

    @auth
    Scenario: Can search date range
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
        When we get "/aapmm?source={"post_filter":{"and":[{"range":{"firstcreated":{"lte":"2015-09-01T14:00:00+00:00","gte":"2015-08-31T14:00:00+00:00"}}}]},"query":{"filtered":{}},"size":48}"
        Then we get list with +1 items
