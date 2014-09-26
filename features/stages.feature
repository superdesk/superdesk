Feature: Stages

    @auth
    Scenario: Add stage
        Given empty "stages"

        When we post to "/stages"
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
        "description": "Show content items created by the current logged user"
        }
        """


    @auth
    Scenario: Add stage - no name
        Given empty "stages"

        When we post to "/stages"
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
    Scenario: Add stage - no description
        Given empty "stages"
        When we post to "/stages"
        """
        {
        "name": "show my content"
        }
        """

        Then we get new resource
        """
        {
        "name": "show my content"
        }
        """

    @auth
    Scenario: Add stage - with desk
        Given empty "stages"

        When we post to "desks"
        """
        {"name": "Sports Desk"}
        """

        When we post to "/stages"
        """
        {
        "name": "show my content",
        "desk": "#DESKS_ID#",
        "description": "Show content items created by the current logged user"
        }
        """

        Then we get new resource
        """
        {
        "name": "show my content",
        "desk": "#DESKS_ID#",
        "description": "Show content items created by the current logged user"
        }
        """

    @auth
    Scenario: Edit stage - modify description and name
        Given empty "stages"

        When we post to "/stages"
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
        "description": "Show content items created by the current logged user"
        }
        """
        When we patch latest
        """
        {
        "description": "Show content that I just updated",
        "name": "My stage"
        }
        """
        Then we get updated response
