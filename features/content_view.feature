Feature: Content View    

    @auth
    Scenario: Add content view 
        Given empty "content_view"

        When we post to "/content_view"
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "location": "archive",
        "roles": ["role1", "role2", "role3"],
        "desks":["desk1", "desk2", "desk3"],
        "filter": "{\"query\":{\"filtered\":{\"query\":{\"match_all\":{}},\"filter\":{\"and\":[{\"terms\":{\"type\":[\"text\",\"picture\"]}}]}}}}"
        }
        """

        Then we get new resource
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "location": "archive",
        "roles": ["role1", "role2", "role3"],
        "desks":["desk1", "desk2", "desk3"],
        "filter": "{\"query\":{\"filtered\":{\"query\":{\"match_all\":{}},\"filter\":{\"and\":[{\"terms\":{\"type\":[\"text\",\"picture\"]}}]}}}}"
        }
        """
        
        
    @auth
    Scenario: Add content view - no name 
        Given empty "content_view"

        When we post to "/content_view"
        """
        {
        "description": "Show content items created by the current logged user",
        "location": "archive",
        "roles": ["role1", "role2", "role3"],
        "desks":["desk1", "desk2", "desk3"],
        "filter": "{\"query\":{\"filtered\":{\"query\":{\"match_all\":{}},\"filter\":{\"and\":[{\"terms\":{\"type\":[\"text\",\"picture\"]}}]}}}}"
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
        "location": "archive",
        "roles": ["role1", "role2", "role3"],
        "desks":["desk1", "desk2", "desk3"],
        "filter": "{\"query\":{\"filtered\":{\"query\":{\"match_all\":{}},\"filter\":{\"and\":[{\"terms\":{\"type\":[\"text\",\"picture\"]}}]}}}}"
        }
        """

        Then we get error 400
		"""
      	{"_error": {"code": 400, "message": "Insertion failure: 1 document(s) contain(s) error(s)"}, "_issues": {"description": {"required": 1}}, "_status": "ERR"}
      	"""
      	        

    @auth
    Scenario: Add content view - no location 
        Given empty "content_view"

        When we post to "/content_view"
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "roles": ["role1", "role2", "role3"],
        "desks":["desk1", "desk2", "desk3"],
        "filter": "{\"query\":{\"filtered\":{\"query\":{\"match_all\":{}},\"filter\":{\"and\":[{\"terms\":{\"type\":[\"text\",\"picture\"]}}]}}}}"
        }
        """

        Then we get error 400
		"""
      	{"_error": {"code": 400, "message": "Insertion failure: 1 document(s) contain(s) error(s)"}, "_issues": {"location": {"required": 1}}, "_status": "ERR"}
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
        "roles": ["role1", "role2", "role3"],
        "desks":["desk1", "desk2", "desk3"],
        "filter": "{\"query\":{\"filtered\":{\"query\":{\"match_all\":{}},\"filter\":{\"and\":[{\"terms\":{\"type\":[\"text\",\"picture\"]}}]}}}}"
        }
        """

        Then we get error 400
		"""
      	{"_error": {"code": 400, "message": "Insertion failure: 1 document(s) contain(s) error(s)"}, "_issues": {"location": "unallowed value wrong_location"}, "_status": "ERR"}
      	"""  
      	

    @auth
    Scenario: Add content view - no desks
        Given empty "content_view"

        When we post to "/content_view"
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "location": "archive",
        "roles": ["role1", "role2", "role3"],
        "filter": "{\"query\":{\"filtered\":{\"query\":{\"match_all\":{}},\"filter\":{\"and\":[{\"terms\":{\"type\":[\"text\",\"picture\"]}}]}}}}"
        }
        """

        Then we get new resource
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "location": "archive",
        "roles": ["role1", "role2", "role3"],
        "filter": "{\"query\":{\"filtered\":{\"query\":{\"match_all\":{}},\"filter\":{\"and\":[{\"terms\":{\"type\":[\"text\",\"picture\"]}}]}}}}"
        }
        """    
        
        
    @auth
    Scenario: Add content view - empty desks list
        Given empty "content_view"

        When we post to "/content_view"
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "location": "archive",
        "roles": ["role1", "role2", "role3"],
        "desks":[],
        "filter": "{\"query\":{\"filtered\":{\"query\":{\"match_all\":{}},\"filter\":{\"and\":[{\"terms\":{\"type\":[\"text\",\"picture\"]}}]}}}}"
        }
        """

        Then we get new resource
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "location": "archive",
        "roles": ["role1", "role2", "role3"],
        "filter": "{\"query\":{\"filtered\":{\"query\":{\"match_all\":{}},\"filter\":{\"and\":[{\"terms\":{\"type\":[\"text\",\"picture\"]}}]}}}}"
        }
        """     
        

    @auth
    Scenario: Add content view - no roles
        Given empty "content_view"

        When we post to "/content_view"
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "location": "archive",
        "desks": ["desks1", "desks2", "desks3"],
        "filter": "{\"query\":{\"filtered\":{\"query\":{\"match_all\":{}},\"filter\":{\"and\":[{\"terms\":{\"type\":[\"text\",\"picture\"]}}]}}}}"
        }
        """

        Then we get new resource
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "location": "archive",
        "desks": ["desks1", "desks2", "desks3"],
        "filter": "{\"query\":{\"filtered\":{\"query\":{\"match_all\":{}},\"filter\":{\"and\":[{\"terms\":{\"type\":[\"text\",\"picture\"]}}]}}}}"
        }
        """    
        
        
    @auth
    Scenario: Add content view - empty roles list
        Given empty "content_view"

        When we post to "/content_view"
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "location": "archive",
        "roles": [],
        "desks":["desks1", "desks2", "desks3"],
        "filter": "{\"query\":{\"filtered\":{\"query\":{\"match_all\":{}},\"filter\":{\"and\":[{\"terms\":{\"type\":[\"text\",\"picture\"]}}]}}}}"
        }
        """

        Then we get new resource
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "location": "archive",
        "desks":["desks1", "desks2", "desks3"],
        "filter": "{\"query\":{\"filtered\":{\"query\":{\"match_all\":{}},\"filter\":{\"and\":[{\"terms\":{\"type\":[\"text\",\"picture\"]}}]}}}}"
        }
        """      
        
        
    @auth
    Scenario: Add content view - no filter
        Given empty "content_view"

        When we post to "/content_view"
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "location": "archive",
        "roles": ["roles1", "roles2", "roles3"],
        "desks":["desks1", "desks2", "desks3"]
        }
        """

        Then we get new resource
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user",
        "location": "archive",
        "roles": ["roles1", "roles2", "roles3"],
        "desks":["desks1", "desks2", "desks3"]
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
        "location": "archive",
        "roles": ["roles1", "roles2", "roles3"],
        "desks":["desks1", "desks2", "desks3"],
        "filter": "{type}"
        }
        """

        Then we get error 400
	    """
	    {"_message": "", "_issues": "Fail to validate the filter against archive. The search returns the following error: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)", "_status": "ERR"}
	    """
	   
 # TODO: fix #  Scenario: Set a role to a user from user.features
 #   @auth
 #   Scenario: View user content view
 #       Given empty "user_roles"
 #       And empty "content_view"
 #
 #      When we post to "/user_roles"
 #          """
 #          {"name": "Editor"}
 #          """
 #
 #      When we patch "/users/test_user"
 #          """
 #          {"role": "#USER_ROLES_ID#"}
 #          """
 #
 #        When we post to "/content_view"
 #       """
 #       {
 #       "name": "show my content",
 #       "description": "Show content items created by the current logged user",
 #       "location": "archive",
 #       "roles": ["#USER_ROLES_ID#"],
 #       "desks":["desks1", "desks2", "desks3"],
 #       "filter": "{type}"
 #       }
 #       """
 #       
 #       # And we get "/user_content_view?location=archive&desk=desk1"
 #       
 #       Then we get existing resource
 #       """
 #       {
 #       "name": "show my content",
 #       "description": "Show content items created by the current logged user",
 #       "location": "archive",
 #       "roles": [],
 #       "desks": ["desks1", "desks2", "desks3"],
 #       "filter": "{\"query\":{\"filtered\":{\"query\":{\"match_all\":{}},\"filter\":{\"and\":[{\"terms\":{\"type\":[\"text\",\"picture\"]}}]}}}}"
 #       }]
 #       """    
                             	    	