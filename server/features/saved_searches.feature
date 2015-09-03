Feature: Saved Searches

    @auth
    Scenario: Create a Saved Search
        Given empty "saved_searches"
        When we post to "/users/#CONTEXT_USER_ID#/saved_searches"
        """
        {
        "name": "cricket",
        "filter": {"query": {"q": "cricket", "repo": "archive"}}
        }
        """
        Then we get response code 201

    @auth
    Scenario: Create a Saved Search with facets
        Given empty "saved_searches"
        When we post to "/users/#CONTEXT_USER_ID#/saved_searches"
        """
        {
        "name": "cricket and text and from AAP",
        "filter":{"query":{"q":"cricket","repo":"ingest","type": ["text"], "source": ["AAP"]}}
        }
        """
        Then we get response code 201

	@auth
    Scenario: A user shouldn't see another user's searches but all saved searches will show them
        Given empty "saved_searches"
        When we post to "/users"
        """
        {"username": "save_search", "display_name": "Joe Black", "email": "joe@black.com", "is_active": true, "sign_off": "abc"}
        """
        And we post to "/users/#users._id#/saved_searches"
        """
        {
        "name": "basket ball",
        "filter": {"query": {"q": "basket ball", "repo": "ingest"}}
        }
        """
        When we post to "/users/#CONTEXT_USER_ID#/saved_searches"
        """
        {
        "name": "cricket",
        "filter": {"query": {"q": "cricket", "repo": "archive"}}
        }
        """
        When we get "/users/#users._id#/saved_searches"
        Then we get list with 1 items
        When we get "/users/#CONTEXT_USER_ID#/saved_searches"
        Then we get list with 1 items

        When we get "/all_saved_searches"
        Then we get list with 2 items

    @auth
    Scenario: Create a Saved Search without a name
        Given empty "saved_searches"
        When we post to "/users/#CONTEXT_USER_ID#/saved_searches"
        """
        {
        "filter": {"query": {"q": "cricket", "repo": "archive"}}
        }
        """
        Then we get error 400
		"""
      	{"_error": {"code": 400, "message": "Insertion failure: 1 document(s) contain(s) error(s)"}, "_issues": {"name": {"required": 1}}, "_status": "ERR"}
      	"""

    @auth
    Scenario: Create a Saved Search without a filter
        Given empty "saved_searches"
        When we post to "/users/#CONTEXT_USER_ID#/saved_searches"
        """
        {
        "name": "cricket"
        }
        """
        Then we get error 400
		"""
      	{"_error": {"code": 400, "message": "Insertion failure: 1 document(s) contain(s) error(s)"}, "_issues": {"filter": {"required": 1}}, "_status": "ERR"}
      	"""

    @auth
    Scenario: Create a Saved Search with invalid filter
        Given empty "saved_searches"
        When we post to "/users/#CONTEXT_USER_ID#/saved_searches"
        """
        {
        "name": "cricket",
        "filter": {"abc": "abc"}
        }
        """
        Then we get error 400
	    """
	    {"_message": "Fail to validate the filter.", "_status": "ERR"}
	    """

	@auth
    Scenario: Update a Saved Search
        Given empty "saved_searches"
        When we post to "/users/#CONTEXT_USER_ID#/saved_searches"
        """
        {
        "name": "cricket",
        "filter": {"query": {"q": "cricket"}}
        }
        """
        Then we get response code 201
        When we patch "/users/#CONTEXT_USER_ID#/saved_searches"
        """
        {
        "name": "Cricket"
        }
        """
        Then we get response code 405

    @auth
    @provider
    Scenario: Create a Saved Search and retrieve content
    	Given empty "ingest"
        When we fetch from "reuters" ingest "tag_reuters.com_2014_newsml_KBN0FL0NM"
        Given empty "saved_searches"
        When we post to "/users/#CONTEXT_USER_ID#/saved_searches"
        """
        {
        "name": "US Pictures",
        "filter": {"query": {"q": "US", "repo": "ingest", "type": ["picture"]}}
        }
        """
        Then we get response code 201
        When we get "/users/#CONTEXT_USER_ID#/saved_searches/#saved_searches._id#"
        Then we get existing resource
        """
        {
        "name": "US Pictures",
        "filter": {"query": {"q": "US", "repo": "ingest", "type": ["picture"]}}
        }
        """
        When we get "/saved_searches/#saved_searches._id#/items"
        Then we get list with 3 items
		"""
		{
		    "_items": [{
		        "type": "picture",
		        "guid": "tag_reuters.com_2014_newsml_LYNXMPEA6F0MS",
		        "state": "ingested"
		    }, {
		        "type": "picture",
		        "guid": "tag_reuters.com_2014_newsml_LYNXMPEA6F0MT",
		        "state": "ingested"
		    }, {
		        "type": "picture",
		        "guid": "tag_reuters.com_2014_newsml_LYNXMPEA6F13M",
		        "state": "ingested"
		    }]
		}
		"""
