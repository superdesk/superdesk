Feature: User Sessions

    @dbauth
    @auth
    Scenario: Get user sessions
        When we post to "/users"
        """
        {"username": "psmith", "password": "12334556", "email": "psmith@psmith.org"}
        """
        Then we get response code 201

        When we post to "/auth"
        """
        {"username": "psmith", "password": "12334556"}
        """
        Then we get new resource
        """
        {"username": "psmith"}
        """
        
        When we get "user_sessions/#users._id#"
        Then we get existing resource
        """
        {"username": "psmith", "session_preferences": {"#auth._id#": {"pinned:items": []}}}
        """
        
    @dbauth
    @auth
	Scenario: Delete user sessions
        When we post to "/users"
        """
        {"username": "psmith", "password": "12334556", "email": "psmith@psmith.org", "user_type": "administrator"}
        """
        Then we get response code 201

        When we post to "/auth"
        """
        {"username": "psmith", "password": "12334556"}
        """
        Then we get new resource
        """
        {"username": "psmith"}
        """
        
        When we delete "/user_sessions/#users._id#"
        Then we get response code 204
        
        When we get "/users/#users._id#"
        Then we get existing resource
        """
        {"username": "psmith", "session_preferences": {}}
        """
        
        When we get "/auth/#auth._id"
        Then we get response code 404
        
        
        
        


	