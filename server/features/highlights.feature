Feature: Highlights

    @auth
    Scenario: Create highlight
        Given "desks"
		"""
		[{"name": "desk1"}]
		"""	
        When we post to "highlights"
        """
        {"name": "highlight1", "desks": ["#desks._id#"]}
        """
        Then we get new resource
        """
        {"name": "highlight1", "desks": ["#desks._id#"]}
        """
        When we get "highlights"
        Then we get list with 1 items
        """
        {"_items": [{"name": "highlight1", "desks": ["#desks._id#"]}]}
        """
        
    @auth
    Scenario: Create duplicate highlight
        Given "desks"
		"""
		[{"name": "desk1"}]
		"""	
        When we post to "highlights"
        """
        {"name": "highlight1", "desks": ["#desks._id#"]}
        """
        When we post to "highlights"
        """
        {"name": "Highlight1", "desks": ["#desks._id#"]}
        """
        Then we get response code 400
            
    @auth
    Scenario: Update highlight
        Given "desks"
		"""
		[{"name": "desk1"}]
		"""	
        When we post to "highlights"
        """
        {"name": "highlight1"}
        """
        When we patch "highlights/#highlights._id#"
        """
        {"name": "highlight changed", "desks": ["#desks._id#"]}
        """
        When we get "highlights"
        Then we get list with 1 items
        """
        {"_items": [{"name": "highlight changed", "desks": ["#desks._id#"]}]}
        """
        
    @auth
    Scenario: Mark item for highlights
        Given "desks"
		"""
		[{"name": "desk1"}]
		"""	
        When we post to "highlights"
        """
        {"name": "highlight1", "desks": ["#desks._id#"]}
        """
        Then we get new resource
        """
        {"name": "highlight1", "desks": ["#desks._id#"]}
        """
        When we post to "archive"
		"""
		[{"headline": "test"}]
		"""	
		When we post to "marked_for_highlights"
		"""
		[{"highlights": "#highlights._id#", "marked_item": "#archive._id#"}]
		"""
		Then we get new resource
        """
        {"highlights": "#highlights._id#", "marked_item": "#archive._id#"}
        """
        When we get "archive"
        Then we get list with 1 items
        """
        {"_items": [{"headline": "test", "highlights": ["#highlights._id#"]}]}
        """

    @auth
    Scenario: Mark not available item for highlights
        Given "desks"
		"""
		[{"name": "desk1"}]
		"""	
        When we post to "highlights"
        """
        {"name": "highlight1", "desks": ["#desks._id#"]}
        """
		When we post to "marked_for_highlights"
		"""
		[{"highlights": "#highlights._id#", "marked_item": "not_available_item_id"}]
		"""
		Then we get new resource
        """
        {"_id": "","highlights": "#highlights._id#", "marked_item": "not_available_item_id"}
        """
        When we get "archive"
        Then we get list with 0 items

                
    @auth
    Scenario: Delete highlights
        Given "desks"
		"""
		[{"name": "desk1"}]
		"""	
        When we post to "highlights"
        """
        {"name": "highlight1", "desks": ["#desks._id#"]}
        """
        When we post to "archive"
		"""
		[{"headline": "test"}]
		"""	
		Then we get new resource
        """
        {"headline": "test"}
        """
		When we post to "marked_for_highlights"
		"""
		[{"highlights": "#highlights._id#", "marked_item": "#archive._id#"}]
		"""
		When we delete "highlights/#highlights._id#"
		Then we get response code 204
		When we get "highlights"
        Then we get list with 0 items
		When we get "archive"
        Then we get list with 1 items
        """
        {"_items": [{"headline": "test", "highlights": []}]}
        """

		