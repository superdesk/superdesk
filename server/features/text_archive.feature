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