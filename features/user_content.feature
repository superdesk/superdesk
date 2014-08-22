Feature: User Content

    @wip
    @auth
    Scenario: List my new content
        Given empty "archive"

        When we post to "/archive"
        """
        {
            "headline": "show my content",
            "type": "text"
        }
        """
        Then we get new resource

        When we get user "content"
        Then we get list with 1 items
        """
        {
          "_items": [{
                "_links": {
                     "self": {
                        "href": "/archive/#ARCHIVE_ID#",
                        "title": "Archive"
                      }
                   }
                }]
        }
        """
		
        When we switch user
        And we get user "content"
        Then we get list with 0 items
