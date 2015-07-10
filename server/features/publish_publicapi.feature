Feature: Publish content to the public API

    @auth
    @notification
    Scenario: Publish a text item
		Given "desks"
		"""
		[{"name": "test_desk1"}]
		"""
        And "archive"
        """
        [{
        	"guid": "item1",
        	"unique_name": "#9028",
        	"version": "1",
        	"type": "text",
        	"original_creator": "#CONTEXT_USER_ID#",
        	"versioncreated": "2015-06-01T22:19:08+0000",
        	"subject": [{"name": "medical research", "parent": "07000000", "qcode": "07005000"}],
        	"anpa_category": [{"qcode": "a"}],
        	"task": {
        		"desk": "#desks._id#",
        		"stage": "#desks.incoming_stage#",
        		"status": "todo",
        		"user": "#CONTEXT_USER_ID#"
        	},
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
		And the "validators"
		"""
		[{"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
		"""
		When we post to "/subscribers" with success
		"""
		{
		  "name":"Channel 3","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
		  "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
		}
		"""
 		And we publish "item1" with "publish" type and "published" state
		Then we get OK response
        And we get notifications
	    """
	    [{"event": "item:publish", "extra": {"item": "item1"}}]
	    """
		And we get existing resource
        """
        {"_current_version": 2, "state": "published", "task":{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}
        """
        When we get "/publish_queue"
        Then we get existing resource
        """
        {"_items": [{"state": "pending"}]}
        """
        When we get "/published"
        Then we get existing resource
        """
        {"_items" : [{"guid": "item1", "_current_version": 2, "state": "published"}]}
        """
