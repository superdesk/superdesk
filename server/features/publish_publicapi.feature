Feature: Publish content to the public API

    @auth
    @notification
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
        # I can see here you are creating an output channel with
        # ninjs format which is good
	    """
	    [{"name": "channel 1", "format": "ninjs", "channel_type": "metadata", "is_active": true, "destinations": ["#subscribers._id#"]}]
	    """
	    Given "destination_groups"
        # This is fine too, destination group has the output channel
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
        # This is the key step where the article is published
        # What we expect at the end of this step:
        # 1- Article will turn into "published" state in archive collection
        # 2- The version of article is created in "published" collection
        # 3- Article is transformed into ninjs and saved into formatted_item collection
        # 4- A new queue entry is created with status "pending".Scenario:
        # 5- item:publish notification is sent
		Then we get OK response
        And we get notifications
	    """
	    [{"event": "item:publish", "extra": {"item": "item1"}}]
	    """
		And we get existing resource
        """
        {"_version": 2, "state": "published", "task":{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}
        """
        When we get "/publish_queue"
        Then we get existing resource
        """
        {"_items": [{"state": "pending"}]}
        """
        When we get "/published"
        Then we get existing resource
        """
        {"_items" : [{"guid": "item1", "_version": 2, "state": "published"}]}
        """
        When we get "/formatted_item"
        Then we get list with 1 items
        """
        {
          "_items":
            [
              {"format": "ninjs"}
            ]
        }
        """

        # At this point everything is fine. We succeded all 5 events above.
        # So my opinion is that when we see "pending" item in queue this test is complete
        # During the application queue_items are polled by a celery task publish:transmit
        # This task gets the items in "pending" state and transmit them.
        # The transmitted items turn into "success", failed ones to "error" with the message
        # I saw your superdesk/publish/publicapi.py and is all good
        # The actual transmission can only be tested at that level, not here
        # One minor thing I noticed is that body_html is not used in ninjs transformation
        # but maybe you have designed it like this

