Feature: User Activity

    @wip
    @auth
    Scenario: User activity
         When we post to "/users"
            """
            {"username": "foo", "password": "barbar", "email": "foo@bar.com"}
            """
            
         Then we get response code 201
         When we get "/activity/"
         Then we get existing resource
         	"""
         	{"_items": [{"data": {"user": "foo"}, "message": "created user {{user}}"}]}
         	"""
         	
         When we delete "/users/foo"
         Then we get response code 200
         
         When we get "/activity/"
         Then we get existing resource
         	"""
         	{"_items": [{"data": {"user": "foo"}, "message": "removed user {{user}}"}]}
         	"""
    
    @wip
    @auth
    Scenario: Image archive activity
        Given empty "archive"
        When we upload a file "bike.jpg" to "archive_media"
     	
     	When we get "/activity/"
        Then we get existing resource
         	"""
         	{"_items": [{"data": {"renditions": {}, "name": "image/jpeg"}, "message": "uploaded media {{ name }}"}]}
         	"""
        