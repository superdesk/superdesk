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

        
    @auth
    Scenario: List my new content when having content with stages
        Given empty "desks"
        Given empty "archive"
        Given empty "tasks"
        Given empty "stages"
        When we post to "/stages"
        """
        {
        "name": "show my content",
        "description": "Show content items created by the current logged user"
        }
        """
        When we post to "desks"
        """
        {"name": "Sports Desk", "incoming_stage": "#STAGES_ID#"}
        """
        When we patch "/stages/#STAGES_ID#"
        """
        {"desk":"#DESKS_ID#"}
        """
        When we post to "archive"
	    """
        [{"slugline": "first doc", "type": "text", "task": {"desk":"#DESKS_ID#", "stage" :"#STAGES_ID#"}}]
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
                        "href": "/archive/#ARCHIVE_ID#",
                        "title": "Archive"
                      }
                   }
                }]
        }
        """
