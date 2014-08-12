Feature: Content View    

    @auth
    Scenario: Add content view 
        Given empty "content_view"

        When we post to "/content_view"
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "filter": {"and":[{"terms":{"type":["text","picture"]}}]}
        }
        """

        Then we get new resource
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "location": "archive",
        "filter": {"and":[{"terms":{"type":["text","picture"]}}]}
        }
        """
        
        
    @auth
    Scenario: Add content view - no name 
        Given empty "content_view"

        When we post to "/content_view"
        """
        {
        "description": "Show content items created by the current logged user"
        }
        """

        Then we get error 400
		"""
      	{"_error": {"code": 400, "message": "Insertion failure: 1 document(s) contain(s) error(s)"}, "_issues": {"name": {"required": 1}}, "_status": "ERR"}
      	"""


    @auth
    Scenario: Add content view - no description 
        Given empty "content_view"

        When we post to "/content_view"
        """
        {
        "name": "show my content",
        "location": "ingest",
        "filter": {"and":[{"terms":{"type":["text","picture"]}}]}
        }
        """

        Then we get new resource
        """
        {
        "name": "show my content",
        "location": "ingest",
        "filter": {"and":[{"terms":{"type":["text","picture"]}}]}
        }
        """
      	
    @auth
    Scenario: Add content view - wrong location 
        Given empty "content_view"

        When we post to "/content_view"
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "location": "wrong_location",
        "filter": {"and":[{"terms":{"type":["text","picture"]}}]}
        }
        """

        Then we get error 400
		"""
      	{"_error": {"code": 400, "message": "Insertion failure: 1 document(s) contain(s) error(s)"}, "_issues": {"location": "unallowed value wrong_location"}, "_status": "ERR"}
      	"""  
      	

    @auth
    Scenario: Add content view - with desk
        Given empty "content_view"

        When we post to "desks"
        """
        {"name": "Sports Desk"}
        """

        When we post to "/content_view"
        """
        {
        "name": "show my content",
        "desk": "#DESKS_ID#",
        "description": "Show content items created by the current logged user",
        "filter": {"and":[{"terms":{"type":["text","picture"]}}]}
        }
        """

        Then we get new resource
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "location": "archive",
        "filter": {"and":[{"terms":{"type":["text","picture"]}}]}
        }
        """    
               

    @auth
    Scenario: Add content view - no filter
        Given empty "content_view"

        When we post to "/content_view"
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user"
        }
        """

        Then we get new resource
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "location": "archive"
        }
        """      
        
    @auth
    Scenario: Add content view - wrong filter
        Given empty "content_view"

        When we post to "/content_view"
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "filter": {"abc": "abc"}
        }
        """

        Then we get error 400
	    """
	    {"_message": "", "_issues": "Fail to validate the filter against archive.", "_status": "ERR"}
	    """

    @auth
    Scenario: Create user content view
        When we post to "/content_view"
            """
            {"name": "test", "filter": {"term": {"headline": "test"}}}
            """

        And we get my "/content_view"

        Then we get list with 1 items
