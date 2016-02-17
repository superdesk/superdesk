Feature: AAP Multimedia Feature

    @auth
    Scenario: Can search multimedia
        Given "search_providers"
	    """
        [{"search_provider": "aapmm", "source": "AAP One", "config": {"password":"", "username":""}}]
	    """
        When we get "/aapmm"
        Then we get list with +1 items

    @auth
    Scenario: Can search fetch from
        Given "search_providers"
	    """
        [{"search_provider": "aapmm", "source": "AAP One", "config": {"password":"", "username":""}}]
	    """
        And "desks"
        """
        [{"name": "Sports"}]
        """
        When we post to "/aapmm"
        """
        {"guid": "20150329001116807745", "desk": "#desks._id#"}
        """
        Then we get response code 201
        When we get "/archive?q=#desks._id#"
        Then we get list with 1 items
        """
        {"_items": [
      	  {
      		  "family_id": "20150329001116807745",
      		  "ingest_id": "20150329001116807745",
      		  "operation": "fetch",
      		  "sign_off": "abc",
      		  "byline": "JULIAN SMITH",
      		  "firstcreated": "2015-03-29T08:49:44+0000"
      	  }
        ]}
        """
        Then we get no "dateline"

    @auth
    Scenario: Can search credit and type facets
        Given "search_providers"
	    """
        [{"search_provider": "aapmm", "source": "AAP One", "config": {"password":"", "username":""}}]
	    """
        When we get "/aapmm?source={"post_filter":{"and":[{"terms":{"type":["image"]}},{"terms":{"credit":["aapimage"]}}]},"query":{"filtered":{}},"size":48}"
        Then we get list with +1 items

    @auth
    Scenario: Can search categories facets
        Given "search_providers"
	    """
        [{"search_provider": "aapmm", "source": "AAP One", "config": {"password":"", "username":""}}]
	    """
        When we get "/aapmm?source={"post_filter":{"and":[{"terms":{"anpa_category.name":["news"]}}]},"query":{"filtered":{}},"size":48}"
        Then we get list with +1 items

    @auth
    Scenario: Can search last week
        Given "search_providers"
	    """
        [{"search_provider": "aapmm", "source": "AAP One", "config": {"password":"", "username":""}}]
	    """
        When we get "/aapmm?source={"post_filter":{"and":[{"range":{"firstcreated":{"gte":"now-1w"}}}]},"query":{"filtered":{}},"size":48}"
        Then we get list with +1 items

    @auth
    Scenario: Can search date range
        Given "search_providers"
	    """
        [{"search_provider": "aapmm", "source": "AAP One", "config": {"password":"", "username":""}}]
	    """
        When we get "/aapmm?source={"post_filter":{"and":[{"range":{"firstcreated":{"lte":"2015-09-01T14:00:00+00:00","gte":"2015-08-31T14:00:00+00:00"}}}]},"query":{"filtered":{}},"size":48}"
        Then we get list with +1 items

    @auth
    Scenario: Deleting a Search Provider isn't allowed after articles have been fetched from this search provider
        Given "search_providers"
	    """
        [{"search_provider": "aapmm", "source": "AAP One", "config": {"password":"", "username":""}}]
	    """
        And "desks"
        """
        [{"name": "Sports"}]
        """
        When we post to "/aapmm"
        """
        {"guid": "20150329001116807745", "desk": "#desks._id#"}
        """
        Then we get response code 201
        When we delete "search_providers/#search_providers._id#"
        Then we get error 403
        """
        {"_status": "ERR", "_message": "Deleting a Search Provider after receiving items is prohibited."}
        """
