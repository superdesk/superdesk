Feature: Ingest Provider

    @auth
    Scenario: List empty providers
        Given empty "ingest_providers"
        When we get "/ingest_providers"
        Then we get list with 0 items

    @auth
    Scenario: Create new ingest_provider
        Given empty "ingest_providers"
        When we post to "ingest_providers"
	    """
        [{
        "type": "reuters",
        "name": "reuters 4",
        "config": {"username": "foo", "password": "bar"}
        }]
	    """
        And we get "/ingest_providers"
        Then we get list with 1 items
	    """
        {"_items": [{
        "type": "reuters",
        "name": "reuters 4",
        "days_to_keep": 2,
        "config": {"username": "foo", "password": "bar"}
        }]}
	    """

    @auth
    Scenario: Update ingest_provider
        Given "ingest_providers"
	    """
        [{
        "type": "reuters",
        "name": "reuters 4",
        "config": {"username": "foo", "password": "bar"}
        }]
	    """
        When we patch given
        """
        {"name":"the test ingest_provider modified", "days_to_keep": 3,
        "config": {"username": "bar", "password": "foo"}}
        """
        And we patch latest
        """
        {"name":"the test of the test ingest_provider modified"}
        """
        Then we get updated response

    @auth
    Scenario: Delete ingest_provider
        Given empty "ingest_providers"
        When we post to "ingest_providers"
	    """
        [{
        "type": "reuters",
        "name": "reuters 4",
        "config": {"username": "foo", "password": "bar"}
        }]
	    """
        And we delete latest
        Then we get deleted response
