Feature: Content View    

    @auth
    Scenario: Add content view - success
        Given empty "content_view"

        When we post to "/content_view"
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "filter": {"query": {"filtered": {"filter": {"and": [{"terms": {"type": ["text", "picture"]}}]}}}}
        }
        """

        Then we get new resource
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "location": "archive",
        "filter": {"query": {"filtered": {"filter": {"and": [{"terms": {"type": ["text", "picture"]}}]}}}}
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
        "filter": {"query": {"filtered": {"filter": {"and": [{"terms": {"type": ["text", "picture"]}}]}}}}
        }
        """

        Then we get new resource
        """
        {
        "name": "show my content",
        "location": "ingest",
        "filter": {"query": {"filtered": {"filter": {"and": [{"terms": {"type": ["text", "picture"]}}]}}}}
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
        "filter": {"query": {"filtered": {"filter": {"and": [{"terms": {"type": ["text", "picture"]}}]}}}}
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
        "filter": {"query": {"filtered": {"filter": {"and": [{"terms": {"type": ["text", "picture"]}}]}}}}
        }
        """

        Then we get new resource
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "location": "archive",
        "filter": {"query": {"filtered": {"filter": {"and": [{"terms": {"type": ["text", "picture"]}}]}}}}
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
    Scenario: Get content view items - check filters
        Given empty "content_view"
        Given empty "archive"

        When we upload a file "bike.jpg" to "archive_media"
        Then we get new resource
        """
        {"guid": "", "firstcreated": "", "versioncreated": ""}
        """

        When we post to "/archive"
        """
        [{"body_html": "test text", "type": "text"}]
        """

        Then we get new resource
        """
        {"_id": "", "guid": "", "body_html": "test text", "type": "text"}
        """

        When we post to "/content_view"
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "filter": {"query": {"filtered": {"query": {"query_string": {"query": "test or samsung"}}, "filter": {"and": [{"terms": {"type": ["text", "picture"]}}]}}}}
        }
        """

        Then we get new resource
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "location": "archive",
        "filter": {"query": {"filtered": {"query": {"query_string": {"query": "test or samsung"}}, "filter": {"and": [{"terms": {"type": ["text", "picture"]}}]}}}}
        }
        """
        
        When we get "/content_view/#CONTENT_VIEW_ID#/items"
        Then we get list with 2 items
        
        When we get "/content_view/#CONTENT_VIEW_ID#/items?source={"query": {"filtered": {"filter": {"and": [{"terms": {"type": ["text", "picture"]}}]}}}}"
        Then we get list with 2 items
        
        When we get "/content_view/#CONTENT_VIEW_ID#/items?source={"query": {"filtered": {"filter": {"and": [{"terms": {"type": ["text"]}}]}}}}"
        Then we get list with 1 items
        
        When we get "/content_view/#CONTENT_VIEW_ID#/items?source={"query": {"filtered": {"filter": {"and": [{"terms": {"type": ["video"]}}]}}}}"
        Then we get list with 0 items
        
        When we get "/content_view/#CONTENT_VIEW_ID#/items?source={"query": {"filtered": {"query": {"query_string": {"query": "test or samsung"}}}}}"
        Then we get list with 2 items
        
        When we get "/content_view/#CONTENT_VIEW_ID#/items?source={"query": {"filtered": {"query": {"query_string": {"query": "test"}}}}}"
        Then we get list with 1 items
        
        When we get "/content_view/#CONTENT_VIEW_ID#/items?source={"query": {"filtered": {"query": {"query_string": {"query": "other"}}}}}"
        Then we get list with 0 items
        

    @auth
    Scenario: Get content view items - check self
        Given empty "content_view"
        Given empty "archive"

        When we post to "/archive"
        """
        [{"guid": "12345678", "body_html": "test text", "type": "text"}]
        """

        Then we get new resource
        """
        {"_id": "12345678", "guid": "12345678", "body_html": "test text", "type": "text"}
        """

        When we post to "/content_view"
        """
        {
        "name": "show test content",
        "description": "Show content that contain test word",
        "filter": {"query": {"filtered": {"query": {"query_string": {"query": "test"}}}}}
        }
        """

        Then we get new resource
        """
        {
        "name": "show test content",
        "description": "Show content that contain test word",
        "location": "archive",
        "filter": {"query": {"filtered": {"query": {"query_string": {"query": "test"}}}}}
        }
        """
        
        When we get "/content_view/#CONTENT_VIEW_ID#/items"
        Then we get list with 1 items
        """
        {
          "_items": [{
              "_links": {
                  "self": {
                      "title": "Archive",
                      "href": "/archive/12345678"
                  }
              },
              "guid": "12345678"
          }]
        }
        """
        
	@auth
    Scenario: Edit content view - modify description and name
        Given empty "content_view"

        When we post to "/content_view"
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "filter": {"query": {"filtered": {"filter": {"and": [{"terms": {"type": ["text", "picture"]}}]}}}}
        }
        """

        Then we get new resource
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "location": "archive",
        "filter": {"query": {"filtered": {"filter": {"and": [{"terms": {"type": ["text", "picture"]}}]}}}}
        }
        """
        When we patch latest
        """
        {
        "description": "Show content that I just updated", 
        "name": "My view"
        }
        """
        Then we get updated response


        