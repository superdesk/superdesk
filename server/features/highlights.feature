Feature: Highlights

    @auth
    Scenario: Create highlight
        Given "desks"
		"""
		[{"name": "desk1"}]
		"""	
        When we post to "highlights"
        """
        {"name": "highlight1", "desks": ["#desks._id#"], "groups": ["group one", "group two"]}
        """
        Then we get response code 201
        Then we get new resource
        """
        {"name": "highlight1", "desks": ["#desks._id#"], "groups": ["group one", "group two"]}
        """
        When we get "highlights"
        Then we get list with 1 items
        """
        {"_items": [{"name": "highlight1", "desks": ["#desks._id#"], "groups": ["group one", "group two"]}]}
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
        {"name": "highlight changed", "desks": ["#desks._id#"], "groups": ["group one", "group two"]}
        """
        When we get "highlights"
        Then we get list with 1 items
        """
        {"_items": [{"name": "highlight changed", "desks": ["#desks._id#"], "groups": ["group one", "group two"]}]}
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
        {"_items": [{"headline": "test", "highlights": ["#highlights._id#"], 
                    "_updated": "#archive._updated#", "_etag": "#archive._etag#"}]}
        """

        When we post to "marked_for_highlights"
        """
        [{"highlights": "#highlights._id#", "marked_item": "marked_item": "#archive._id#"}]
        """
        And we get "archive"
        Then we get list with 1 items
        """
        {"_items": [{"highlights": [], "_updated": "#archive._updated#", "_etag": "#archive._etag#"}]}
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
        {"_id": "__any_value__","highlights": "#highlights._id#", "marked_item": "not_available_item_id"}
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

    @auth
    Scenario: Generate text item from highlights
        Given "desks"
        """
        [{"name": "desk1"}]
        """
        Given "archive"
        """
        [
            {"guid": "item1", "type": "text", "headline": "item1", "body_html": "<p>item1 first</p><p>item1 second</p>", "task": {"desk": "#desks._id#"}},
            {"guid": "item2", "type": "text", "headline": "item2", "body_html": "<p>item2 first</p><p>item2 second</p>", "task": {"desk": "#desks._id#"}}
        ]
        """ 
		When we post to "archive"
		"""
		{   "guid": "package",
		    "type": "composite",
		    "headline": "highlights",
		    "groups": [{
		        "id": "root",
		        "refs": [{
		            "idRef": "main"
		        }]
		    }, {
		        "id": "main",
		        "refs": [{
		            "residRef": "item1"
		        }, {
		            "residRef": "item2"
		        }]
		    }],
		    "task": {
		        "desk": "#desks._id#"
		    }
		}
		"""
		
        Then we get new resource
        """
        {"_id": "__any_value__", "type": "composite", "headline": "highlights"}
        """
			
        When we post to "generate_highlights"
        """
        {"package": "package"}
        """

        Then we get new resource
        """
        {"_id": "__any_value__", "type": "text", "headline": "highlights", "body_html": "<h2>item1</h2>\n<p>item1 first</p>\n<p></p>\n<h2>item2</h2>\n<p>item2 first</p>\n<p></p>"}
        """

        When we get "/archive"
        Then we get list with 4 items

        When we post to "generate_highlights"
        """
        {"package": "package", "preview": true}
        """
        Then we get new resource
        """
        {"type": "text"}
        """

    @auth
    Scenario: Prepopulate highlights when creating a package
        Given highlights
        When we create highlights package
        Then we get new package with items
