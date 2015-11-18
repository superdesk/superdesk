Feature: User Content

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
                        "href": "/archive/#archive._id#",
                        "title": "Archive"
                      }
                   }
                }]
        }
        """
		
        When we switch user
        And we get user "content"
        Then we get list with 0 items

    @auth
    Scenario: List my new content when having content with stages Given empty "desks"
        Given empty "archive"
        Given empty "tasks"
        Given empty "stages"
        Given "desks"
        """
        [{"name": "Sports Desk"}]
        """

        When we post to "archive"
	    """
        [{"slugline": "first doc", "type": "text", "task": {"desk":"#desks._id#", "stage" :"#desks.incoming_stage#"}}]
	    """
        When we post to "archive"
        """
        [{"slugline": "second doc", "type": "text"}]
        """
        When we get user "content"
        Then we get list with 1 items
        """
        {
          "_items": [{
                "_links": {
                     "self": {
                        "href": "/archive/#archive._id#",
                        "title": "Archive"
                      }
                   }
                }]
        }
        """

    @wip
    @auth
    Scenario: Hide new content version 0
        When we post to "/archive"
        """
        {"type": "text", "version": 0, "guid": "item1"}
        """
        Then we get new resource
        """
        {"_current_version": 0, "version": 0}
        """

        When we get user "content"
        Then we get list with 0 items

        When we patch "/archive/item1"
        """
        {"headline": "test"}
        """
        Then we get updated response
        """
        {"_current_version": 1, "version": 1}
        """

        When we get user "content"
        Then we get list with 1 items
