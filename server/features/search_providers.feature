Feature: Search Provider Feature

    @auth
    Scenario: List empty providers
        Given empty "search_providers"
        When we get "/search_providers"
        Then we get list with 0 items

    @auth
    Scenario: Create a new Search Provider
        Given empty "search_providers"
        When we post to "search_providers"
	    """
        [{"search_provider": "aapmm", "source": "aapmm", "config": {"password":"", "username":""}}]
	    """
        And we get "/search_providers"
        Then we get list with 1 items
	    """
        {"_items": [{"search_provider": "aapmm", "source": "aapmm", "is_closed": false, "config": {"password":"", "username":""}}]}
	    """

    @auth
    Scenario: Creating a Search Provider fails if the search provider type hasn't been registered with the application
        Given empty "search_providers"
        When we post to "search_providers"
	    """
        [{"search_provider": "aapmm", "source": "aapmm", "config": {"password":"", "username":""}}]
	    """
        And we get "/search_providers"
        Then we get list with 1 items
	    """
        {"_items": [{"search_provider": "aapmm", "source": "aapmm", "is_closed": false, "config": {"password":"", "username":""}}]}
	    """
        When we post to "search_providers"
	    """
        [{"search_provider": "Multimedia", "source": "aapmm", "config": {"password":"", "username":""}}]
	    """
        Then we get error 400
        """
        {"_status": "ERR", "_issues": {"search_provider": "unallowed value Multimedia"}}
        """

    @auth
    Scenario: Creating a Search Provider with same type more than once fails
        Given empty "search_providers"
        When we post to "search_providers"
	    """
        [{"search_provider": "aapmm", "source": "aapmm", "config": {"password":"", "username":""}}]
	    """
        And we get "/search_providers"
        Then we get list with 1 items
	    """
        {"_items": [{"search_provider": "aapmm", "source": "aapmm", "is_closed": false, "config": {"password":"", "username":""}}]}
	    """
        When we post to "search_providers"
	    """
        [{"search_provider": "aapmm", "source": "aapmm", "config": {"password":"", "username":""}}]
	    """
        Then we get error 400
        """
        {"_status": "ERR", "_issues": {"search_provider": {"unique": 1}}}
        """

    @auth
    Scenario: Updating an existing search provider fails if the search provider type hasn't been registered with the application
        Given empty "search_providers"
        When we post to "search_providers"
	    """
        [{"search_provider": "aapmm", "source": "aapmm", "config": {"password":"", "username":""}}]
	    """
        And we get "/search_providers"
        Then we get list with 1 items
	    """
        {"_items": [{"search_provider": "aapmm", "source": "aapmm", "is_closed": false, "config": {"password":"", "username":""}}]}
	    """
        When we patch "search_providers/#search_providers._id#"
        """
        {"search_provider": "Multimedia", "source": "AAP Multimedia"}
        """
        Then we get error 400
        """
        {"_status": "ERR",  "_issues": {"search_provider": "unallowed value Multimedia"}}
        """

    @auth
    Scenario: Deleting a Search Provider is allowed if no articles have been fetched from this search provider
        Given empty "search_providers"
        When we post to "search_providers"
	    """
        [{"search_provider": "aapmm", "source": "aapmm", "config": {"password":"", "username":""}}]
	    """
        And we get "/search_providers"
        Then we get list with 1 items
	    """
        {"_items": [{"search_provider": "aapmm", "source": "aapmm", "is_closed": false, "config": {"password":"", "username":""}}]}
	    """
        When we delete "search_providers/#search_providers._id#"
        Then we get response code 204
