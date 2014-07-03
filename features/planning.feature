Feature: News Items Planning

    @auth
    Scenario: List empty planning
        Given empty "planning"
        When we get "/planning"
        Then we get list with 0 items
        
        
    @auth
    Scenario: Create new planning item
        Given empty "planning"
        When we post to "/planning"
        """
        [{"type": "text", "headline": "testItem", "creditline": "friend Bob"}]
        """
        Then we get new resource
        """
        {"_id": "", "guid": "", "type": "text"}
        """
        
    @auth
    Scenario: Update planning item
        Given "planning"
        """
        [{"_id": "abc", "guid": "testid", "headline": "testItem"}]
        """
        
        When we patch given
        """
        {"slugline": "test1", "urgency": 5, "version": "1"}
        """

        And we patch latest
        """
        {"slugline": "test of the test1", "version": "2"}
        """

        Then we get updated response
