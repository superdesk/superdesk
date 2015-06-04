Feature: Publish content to the public API

    @auth
    Scenario: Publish a text item
	    Given empty "formatted_item"
        Given empty "stages"
		Given "desks"
		"""
		[{"name": "test_desk1"}]
		"""
	    Given "subscribers"
	    """
	    [{"name": "My subscriber", "destinations": [{"delivery_type": "PublicArchive", "name": "Publish"}]}]
	    """
	    Given "output_channels"
	    """
	    [{"name": "channel 1", "format": "ninjs", "channel_type": "metadata", "is_active": true, "destinations": ["#subscribers._id#"]}]
	    """
	    Given "destination_groups"
	    """
	    [{
	        "name":"Group 1", "description": "new stuff",
	        "destination_groups": [],
	        "output_channels": [{"channel":"#output_channels._id#", "selector_codes": ["PXX", "XYZ"]}]
	    }]
	    """
		Given the "validators"
		"""
		[{"_id": "publish", "schema":{}}]
		"""
        Given "archive"
        """
        [{
        	"guid": "item1",
        	"unique_name": "#9028",
        	"version": "1",
        	"type": "text",
        	"original_creator": "#CONTEXT_USER_ID#",
        	"versioncreated": "2015-06-01T22:19:08+0000",
        	"subject": [{"name": "medical research", "parent": "07000000", "qcode": "07005000"}],
        	"anpa-category": {"qcode": "a"},
        	"task": {
        		"desk": "#desks._id#",
        		"stage": "#desks.incoming_stage#",
        		"status": "todo",
        		"user": "#CONTEXT_USER_ID#"
        	},
        	"destination_groups": ["#destination_groups._id#"],
        	"state": "submitted",
        	"pubstatus": "usable",
        	"urgency": 1,
        	"byline": "John Doe",
        	"language": "en",
        	"headline": "some headline",
        	"slugline": "some slugline",
        	"body_html": "item content"
        }]
        """
 		When we publish "item1" with "publish" type and "published" state
		Then we get OK response
		And we get existing resource
        """
        {"version": 2, "state": "published", "task":{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}
        """
        When we get "/publish_queue"
        Then we get existing resource
        """
        {"_items": [{"state": "success"}]}
        """
	    And we get notifications
	    """
	    [{"event": "publish_queue:update", "extra": {"queue_id": "#publish_queue._id#", "state": "success"}}]
	    """
	    When we get "/publish_items/item1"
	    Then we get existing resource
        """
        {
        	"_id": "item1",
        	"version": "1",
        	"type": "text",
        	"versioncreated": "2015-06-01T22:19:08+0000",
        	"subject": [{"name": "medical research", "parent": "07000000", "qcode": "07005000"}],
        	"state": "submitted",
        	"pubstatus": "usable",
        	"urgency": 1,
        	"byline": "John Doe",
        	"language": "en",
        	"headline": "some headline",
        	"slugline": "some slugline",
        	"body_html": "item content"
        }
        """
