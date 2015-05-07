Feature: Text Archive

#    @auth
#    Scenario: List empty text archive
#        Given empty "text_archive"
#        When we get "/text_archive"
#        Then we get list with 0 items

    @auth
    Scenario: Create new text archive entry
        Given empty "text_archive"
        When we post to "/text_archive"
	    """
        [{
          "type": "text",
          "guid": "123"
        }]
	    """
        And we get "/text_archive"
        Then we get list with 1 items
	    """
        {
            "_items": [
                {
                  "type": "text",
                  "guid": "123"
        }]
        }
	    """

    @auth
    Scenario: Delete Item from text archive
        Given empty "text_archive"
        When we post to "/text_archive"
	    """
        [{
          "type": "text",
          "guid": "123"
        }]
	    """
        When we patch "/users/#CONTEXT_USER_ID#"
        """
        {"user_type": "user", "privileges": {"textarchive": 1, "archive": 1, "unlock": 1, "tasks": 1, "users": 1}}
        """
        Then we get response code 200
        When we get "/text_archive"
        Then we get list with 1 items
	    """
        {
            "_items": [
                {
                  "type": "text",
                  "guid": "123"
        }]
        }
	    """
        When we delete "/text_archive/#text_archive._id#"
        Then we get response code 204

    @auth
    Scenario: Attempt to delete from text archive with no privilege
        Given empty "text_archive"
        When we post to "/text_archive"
	    """
        [{
          "type": "text",
          "guid": "123"
        }]
	    """
        When we patch "/users/#CONTEXT_USER_ID#"
        """
        {"user_type": "user", "privileges": {"textarchive": 0, "archive": 1, "unlock": 1, "tasks": 1, "users": 1}}
        """
        Then we get response code 200
        When we get "/text_archive"
        Then we get list with 1 items
	    """
        {
            "_items": [
                {
                  "type": "text",
                  "guid": "123"
        }]
        }
	    """
        When we delete "/text_archive/#text_archive._id#"
        Then we get response code 403